from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets

from .serializers import CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer
from reviews.models import Category, Genre, Title, Review, Comment



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = (IsAuthenticatedOrReadOnly, )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes = (IsAuthenticatedOrReadOnly, )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    # permission_classes = (IsAuthenticatedOrReadOnly, )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    #
    # def get_queryset(self):
    #     title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
    #     return title.reviews.all()
    #
    # def perform_create(self, serializer):
    #     title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
    #     serializer.save(post=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
