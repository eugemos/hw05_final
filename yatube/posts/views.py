from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from users.models import User
from .models import Post, Group
from .forms import PostForm, CommentForm
from .utils import make_page_obj
from .constants import (NUMBER_OF_POSTS_ON_MAIN_PAGE,
                        NUMBER_OF_POSTS_ON_GROUP_PAGE,
                        NUMBER_OF_POSTS_ON_USER_PAGE,
                        )


def index(request):
    """Обеспечивает отображение главной страницы."""
    posts = Post.objects.select_related('group')
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_MAIN_PAGE)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Обеспечивает отображение страницы группы slug."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related(
        'author',
    ).filter(
        group=group,
    )
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_GROUP_PAGE)
    context = {
        'page_obj': page_obj,
        'group': group,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Обеспечивает отображение страницы пользователя username."""
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'group',
    ).filter(
        author=author,
    )
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_USER_PAGE)
    context = {
        'page_obj': page_obj,
        'author': author,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Обеспечивает отображение страницы записи post_id."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Обеспечивает отображение страницы создания новой записи."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            reverse('posts:profile', args=[request.user.username])
        )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Обеспечивает отображение страницы редактирования записи post_id."""
    post = get_object_or_404(Post, id=post_id)
    if post.author.username != request.user.username:
        return redirect(
            reverse('posts:post_detail', args=[post_id])
        )

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )
    if request.method == 'POST' and form.is_valid():
        post.save()
        return redirect(
            reverse('posts:post_detail', args=[post_id])
        )

    context = {'form': form, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Обрабатывает запрос на создание комментария к записи."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)
