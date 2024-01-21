from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail
# Create your views here.

# same as postlist, but using class based views


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/post_list.xhtml'


""" def post_list(request):
    post_list_result = Post.published.all()
    # pagination with 3 posts per page
    paginator = Paginator(post_list_result, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page number is not an inteer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/post_list.xhtml', {'posts': posts}) """


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/post_detail.xhtml', {'post': post})


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
