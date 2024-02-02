from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden


from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post, User


POSTS_ON_PAGE = 10


def base_posts_query(username=None):
    """Функция отвечающая за формирования основного запроса по постам."""
    base_query = Post.objects.select_related(
        'author', 'location', 'category'
    )

    if username:
        author_id = User.objects.get(username=username)
        base_query = base_query.filter(author__exact=author_id.pk)
    else:
        base_query = base_query.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    return base_query


class BasicPostViewMixin:
    model = Post
    queryset = base_posts_query()


class AlterPostViewMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


# Классы и функции для управления постами.

class PostListView(BasicPostViewMixin, ListView):
    """Вид для главной страницы."""

    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class PostDetailView(BasicPostViewMixin, DetailView):
    """Вид для показа страницы отдельного поста."""

    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')

        return context


class PostCreateView(LoginRequiredMixin, AlterPostViewMixin, CreateView):
    """Класс для создания поста."""

    def form_valid(self, form):
        """Заполняет автора поста."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Редирект на созданный пост."""
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, AlterPostViewMixin, UpdateView):
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


class PostDeleteView(LoginRequiredMixin, AlterPostViewMixin, DeleteView):
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
    paginate_by = POSTS_ON_PAGE

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
    comment = get_object_or_404(Comment, pk=pk_comment)

    if request.user != comment.author:
        return HttpResponseForbidden(render(request, '403.html'))

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

    instance = get_object_or_404(Comment, pk=pk_comment)

    context = {'comment': instance}

    if request.method == 'GET':
        return render(request, 'blog/comment.html', context)

    elif request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk_post)

# Функции связанные с пользователем и его профилем.

def user_profile(request, username):
    profile = get_object_or_404(User.objects.all(), username=username)
    paginator = Paginator(base_posts_query(username=username), POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/profile.html',
        context={'profile': profile, 'page_obj': page_obj},
    )


@login_required
def edit_profile(request, username):

    instance = get_object_or_404(User, username=username)

    if request.user != instance:
        # return HttpResponseForbidden(render(request, '403.html'))
        return redirect(reverse('blog:profile', kwargs={'username': username}))

    form = UserEditForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()
        return redirect(reverse('blog:profile', kwargs={'username': username}))

    context = {'form': form}
    return render(request, 'blog/user.html', context)
