from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page

from users.models import User
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from .utils import make_page_obj
from .constants import (NUMBER_OF_POSTS_ON_MAIN_PAGE,
                        NUMBER_OF_POSTS_ON_GROUP_PAGE,
                        NUMBER_OF_POSTS_ON_USER_PAGE,
                        )


@cache_page(20, key_prefix='index_page')
def index(request):
    """Отображает главную страницу."""
    posts = Post.objects.select_related('group')
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_MAIN_PAGE)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отображает страницу группы slug."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_GROUP_PAGE)
    context = {
        'page_obj': page_obj,
        'group': group,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображает страницу пользователя username."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_USER_PAGE)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отображает страницу записи post_id."""
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
    """Отображает страницу создания новой записи."""
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
    """Отображает страницу редактирования записи post_id."""
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


@login_required
def follow_index(request):
    """Отображает страницу с постами авторов, на которых подписан текущий
    пользователь.
    """
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related(
        'group'
    )
    page_obj = make_page_obj(request, posts, NUMBER_OF_POSTS_ON_MAIN_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Обрабатывает запрос на создание подписки на автора username."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(author=author, user=user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Обрабатывает запрос на удаление подписки на автора username."""
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(author=author, user=user).delete()
    return redirect('posts:profile', username=username)
