from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Comment, Post, User


class FutureDateTimeValidator:
    def __call__(self, value):
        if value < timezone.now():
            raise ValidationError('Нельзя выложить пост из прошлого.')


class UserEditForm(forms.ModelForm):
    """Форма для изменения данных пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class PostForm(forms.ModelForm):
    """Форма для добавления поста."""

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'is_published',)

        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Ворма для добавления комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
