from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count

# same as postlist, but using class based views


""" class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/post_list.xhtml' """


def post_list(request, tag_slug=None):
    post_list_result = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list_result = post_list_result.filter(tags__in=[tag])
    # pagination with 3 posts per page
    paginator = Paginator(post_list_result, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/post_list.xhtml',
                  {'posts': posts,
                   'tag': tag
                   })


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by(
        '-same_tags', '-publish'
    )[:4]

    return render(request, 'blog/post/post_detail.xhtml',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts
                   })


def post_share(request, post_id):
    # retrieve post by id
    post_to_share = get_object_or_404(
        Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(
                post_to_share.get_absolute_url()
            )

            subject = f"{cd['name']} recommends you read {post_to_share.title}"
            message = f"Read {post_to_share.title} at {post_url}\\n"\
                f"{cd['name']}\'s comments:{cd['comments']}"
            send_mail(subject, message, 'fmg3ckali@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.xhtml', {'post': post_to_share,
                                                     'form': form,
                                                     'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a comment object without saving it to the database
        comment = form.save(commit=False)
        # assign the post to the comment
        comment.post = post
        # save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.xhtml',
                  {
                      'post': post,
                      'form': form,
                      'comment': comment
                  })
