from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, UserEditForm
from .mixins import AlterPostViewMixin, BasicPostViewMixin, CreatePostViewMixin
from .models import Category, Comment, Post, User
from .utils import base_posts_query


# Классы и функции для управления постами.

class PostListView(BasicPostViewMixin, ListView):
    """Вид для главной страницы."""

    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_ON_PAGE


class PostDetailView(DetailView):
    """Класс для представления отдельного поста."""

    template_name = 'blog/detail.html'

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.user == post.author:
            context = {
                'post': post,
                'form': CommentForm(),
                'comments': post.comments.select_related('author'),
            }
            return render(request, self.template_name, context)
        elif (post.is_published and post.category.is_published
              and post.pub_date < timezone.now()):
            context = {
                'post': post,
                'form': CommentForm(),
                'comments': post.comments.select_related('author'),
            }
            return render(request, self.template_name, context)
        else:
            raise Http404("Page not found")


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
        return reverse('blog:post_detail', kwargs={'pk': self.object.id})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.test_func():
            return redirect('blog:post_detail', pk=self.object.id)
        return super().get(request, *args, **kwargs)


class PostDeleteView(AlterPostViewMixin, DeleteView):
    """Класс для удаления поста."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = self.get_object()
        return context

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(instance=self.object)
        context = self.get_context_data(
            object=self.object,
            form=form,
            instance=form.instance,
        )
        return self.render_to_response(context)


class PostByCategoryView(ListView):
    """Класс для представления постов по категориям."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POSTS_ON_PAGE

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
        category = self.get_category()
        return base_posts_query().filter(category=category)

    def get_context_data(self, **kwargs):
        """Переопределенный метотд для передачи категории в контекст."""
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context['category'] = category
        return context


# Функции управления комментарими.

@login_required
def add_comment(request, pk):
    """Добавление комментария."""
    post_commented = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_commented = post_commented
        comment.save()

    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, pk_post, pk_comment):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, pk=pk_comment)

    if request.user != comment.author:
        return redirect('blog:post_detail', pk_post)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk_post)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment},
    )


@login_required
def delete_comment(request, pk_post, pk_comment):
    """Удаление комментария."""
    instance = get_object_or_404(Comment, pk=pk_comment)

    context = {'comment': instance}

    if request.user != instance.author:
        return redirect('blog:post_detail', pk_post)

    if request.method == 'GET':
        return render(request, 'blog/comment.html', context)

    elif request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk_post)


# Функции связанные с пользователем и его профилем.

def user_profile(request, username):
    """Генерация страницы профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    base_query = base_posts_query(username=username)

    if not request.user == profile_user:
        base_query = base_query.filter(is_published=True)

    paginator = Paginator(base_query, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/profile.html',
        context={'profile': profile_user, 'page_obj': page_obj},
    )


# @login_required
def edit_profile(request, username):
    """Редактирование профиля пользователя."""
    instance = get_object_or_404(User, username=username)

    if request.user != instance:
        return redirect(reverse('blog:profile', kwargs={'username': username}))

    form = UserEditForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()
        return redirect(reverse('blog:profile', kwargs={'username': username}))

    context = {'form': form}
    return render(request, 'blog/user.html', context)
