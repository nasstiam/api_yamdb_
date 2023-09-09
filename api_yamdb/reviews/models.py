import datetime

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError


User = get_user_model()
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


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50, verbose_name='username')
    email = models.EmailField(max_length=200)
    USER = 1
    MODERATOR = 2
    ADMIN = 3
    USER_ROLE_CHOICES = (
        (USER, "user"),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )
    role = models.CharField(max_length=50, choices=USER_ROLE_CHOICES, verbose_name='user_role')
    bio = models.CharField(max_length=200, verbose_name='user_bio', null=True)
    first_name = models.CharField(max_length=200, verbose_name='first_name', null=True)
    last_name = models.CharField(max_length=200, verbose_name='last_name', null=True)

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='category_name')
    slug = models.SlugField(unique=True, verbose_name='slug')

    def __str__(self):
        return self.name


class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='genre_name')
    slug = models.SlugField(unique=True, verbose_name='slug')

    def __str__(self):
        return self.name


class Title(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='title_name')
    year = models.IntegerField(verbose_name='creation_date')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if self.year > datetime.date.today().year:
            raise ValidationError("The year cannot be in the future!")
        elif self.year <= 0:
            raise ValidationError("Invalid year")
        super(Title, self).save(*args, **kwargs)


class GenreTitle(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='genre_title')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_title')


class Review(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name='text_review')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.CharField(max_length=2, choices=SCORE_CHOICES)
    pub_date = models.DateTimeField(
        'Publication date', auto_now_add=True, db_index=True)


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        'Publication date', auto_now_add=True, db_index=True)
