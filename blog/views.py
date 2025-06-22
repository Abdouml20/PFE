from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from .models import BlogPost
from .forms import BlogPostForm
from django.db.models import Count

# List all blog posts with pagination and filter
def blog_list(request):
    filter_by = request.GET.get('filter', 'latest')
    if filter_by == 'most_liked':
        posts = BlogPost.objects.annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')
    else:
        posts = BlogPost.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/blog_list.html', {'page_obj': page_obj, 'filter_by': filter_by})

# Create a blog post (artist only)
@login_required
def blog_create(request):
    if request.user.role != 'artist':
        return HttpResponseForbidden('Only artists can create blog posts.')
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('blog:blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_create.html', {'form': form})

# Like or unlike a post (login required)
@login_required
def like_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})
