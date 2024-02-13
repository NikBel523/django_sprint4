from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserEditForm
from .mixins import (
    AlterPostViewMixin, CreatePostViewMixin, PaginatePostViewMixin
)
from .models import Category, Comment, Post, User
from .queries import post_query_default


# Классы и функции для управления постами.


class PostListView(PaginatePostViewMixin, ListView):
    """Вид для главной страницы."""

    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = post_query_default(filters=True, annotate=True)
        return queryset


class PostByCategoryView(PaginatePostViewMixin, ListView):
    """Класс для представления постов по категориям."""

    template_name = 'blog/category.html'

    def get_category(self):
        """Метод для получения конкретной категории."""
        category_slug = self.kwargs['category_slug']
        return get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True,
        )

    def get_queryset(self):
        """Переопределенный метотд для формирования постов по категории."""
        return (
            post_query_default(
                manager=self.get_category().posts,
                filters=True,
                annotate=True,
            )
        )

    def get_context_data(self, **kwargs):
        """Переопределенный метотд для передачи категории в контекст."""
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context['category'] = category
        return context


class PostDetailView(DetailView):
    """Класс для представления отдельного поста."""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        if (self.request.user == post.author
            or (post.is_published and post.category.is_published
                and post.pub_date < timezone.now())):
            return post
        raise Http404("Page not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(CreatePostViewMixin, CreateView):
    """Класс для создания поста."""

    def form_valid(self, form):
        """Заполняет автора поста."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Редирект на созданный пост."""
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(AlterPostViewMixin, UpdateView):
    """Класс для изменения поста."""

    def get_success_url(self):
        """Редирект на измененный пост."""
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(AlterPostViewMixin, DeleteView):
    """Класс для удаления поста."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


# Функции управления комментарими.

@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    instance = get_object_or_404(Comment, pk=comment_id, post=post_id)

    context = {'comment': instance}

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'GET':
        return render(request, 'blog/comment.html', context)

    elif request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id)


# Функции связанные с пользователем и его профилем.

def user_profile(request, username):
    """Генерация страницы профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        base_query = post_query_default(
            manager=profile_user.posts,
            filters=True,
            annotate=True,
        )
    else:
        base_query = post_query_default(
            manager=profile_user.posts,
            annotate=True,
        )

    paginator = Paginator(base_query, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/profile.html',
        context={'profile': profile_user, 'page_obj': page_obj},
    )


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    form = UserEditForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect(reverse(
            'blog:profile',
            kwargs={'username': request.user},
        ))

    context = {'form': form}
    return render(request, 'blog/user.html', context)


# Класс для формирования страницы регистрации

class UserCreateView(CreateView):
    """Регистрация пользователя."""

    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('pages:rules')
