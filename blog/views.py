from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def post_list(request):
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
    return render(request, 'blog/post/post_list.xhtml', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/post_detail.xhtml', {'post': post})
