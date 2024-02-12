from django import forms

from .models import Comment, Post, User


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
        exclude = ('author',)

        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
        }


class CommentForm(forms.ModelForm):
    """Ворма для добавления комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
