from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail',
    ),
    path(
        'category/<slug:category_slug>/',
        views.PostByCategoryView.as_view(),
        name='category_posts'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post',
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post',
    ),
    path(
        'posts/<int:pk>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path(
        'posts/<int:pk_post>/edit_comment/<int:pk_comment>/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        'posts/<int:pk_post>/delete_comment/<int:pk_comment>/',
        views.delete_comment,
        name='delete_comment',
    ),
    path(
        'profile/<slug:username>/',
        views.user_profile,
        name='profile',
    ),
    path(
        'profile/<slug:username>/edit/',
        views.edit_profile,
        name='edit_profile',
    ),
]
