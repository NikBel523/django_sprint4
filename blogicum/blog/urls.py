from django.urls import include, path

from . import views

app_name = 'blog'

# Пути для работы с постами

posts_urls = [
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail',
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='create_post',
    ),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post',
    ),
    path(
        '<int:post_id>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment',
    ),
]

# Общие пути приложения blog

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'auth/registration/',
        views.UserCreateView.as_view(),
        name='registration',
    ),
    path('posts/', include(posts_urls)),
    path(
        'category/<slug:category_slug>/',
        views.PostByCategoryView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<slug:username>/',
        views.user_profile,
        name='profile',
    ),
    path(
        'profile-edit/edit/',
        views.edit_profile,
        name='edit_profile',
    ),
]
