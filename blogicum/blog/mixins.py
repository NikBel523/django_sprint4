from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .utils import base_posts_query
from .models import Post
from .forms import PostForm


class BasicPostViewMixin:
    """Базовый миксин для представлений модели Post."""

    model = Post
    queryset = base_posts_query()


class CreatePostViewMixin(LoginRequiredMixin):
    """Миксин для форм создания изменения и удаления постов."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class AlterPostViewMixin(CreatePostViewMixin):
    """Миксин для изменения и удаления постов."""

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])

        if post.author != self.request.user:
            return redirect(
                "blog:post_detail", pk=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)
