import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


SCORE_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10')
)


class User(AbstractUser):
    username = models.CharField(max_length=50, verbose_name='username', unique=True)
    email = models.EmailField(max_length=200, unique=True)
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER_ROLE_CHOICES = (
        (USER, "user"),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )
    role = models.CharField(max_length=50, choices=USER_ROLE_CHOICES, default='user', verbose_name='user_role')
    bio = models.CharField(max_length=200, verbose_name='user_bio', null=True)
    first_name = models.CharField(max_length=200, verbose_name='first_name', null=True)
    last_name = models.CharField(max_length=200, verbose_name='last_name', null=True)
    confirmation_code = models.CharField(max_length=36, verbose_name='confirmation_code', null=True)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='category_name')
    slug = models.SlugField(unique=True, verbose_name='slug')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, verbose_name='genre_name')
    slug = models.SlugField(unique=True, verbose_name='slug')

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='title_name')
    year = models.IntegerField(verbose_name='creation_date')
    description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title',
        null=True
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    def save(self, *args, **kwargs):
        """Check year is not negative or not in the future"""
        if self.year > datetime.date.today().year:
            raise ValidationError("The year cannot be in the future!")
        elif self.year <= 0:
            raise ValidationError("Invalid year")
        super(Title, self).save(*args, **kwargs)


class GenreTitle(models.Model):
    """Additional class linking titles and genres"""
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='genre_title')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_title')


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name='text_review')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.CharField(max_length=2, choices=SCORE_CHOICES)
    pub_date = models.DateTimeField(
        'Publication date', auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [["title", "author"]] # author can leave only one review on title


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        'Publication date', auto_now_add=True, db_index=True)
