from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model

TITLE_MAX_LENGTH = 256
TITLE_MAX_LENGTH_VIEW = 20

User = get_user_model()


class BaseModel(models.Model):
    """
    Абстрактная модель. Добавляет каждому объекту:
      -флаг is_published
      -время создания.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """Модель для работы с категориями."""

    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Заголовок',
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы,'
                   ' цифры, дефис и подчёркивание.'),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:TITLE_MAX_LENGTH_VIEW]


class Location(BaseModel):
    """Модель для работы с локациями."""

    name = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:TITLE_MAX_LENGTH_VIEW]


class PostManager(models.Manager):
    def with_comment_count(self):
        return self.annotate(comment_count=Count('comments'))


class Post(BaseModel):
    """Модель для работы с публикациями."""

    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Заголовок',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — можно делать '
                   'отложенные публикации.'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    @property
    def comment_count(self):
        return self.comments.count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.title[:TITLE_MAX_LENGTH_VIEW]


class Comment(models.Model):
    """Модель для пользовательских комментариев."""

    text = models.TextField(verbose_name='Текст')
    post_commented = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
        default_related_name = 'comments'

    def __str__(self) -> str:
        return self.title[:TITLE_MAX_LENGTH_VIEW]
