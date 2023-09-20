from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, Comment, User, GenreTitle


class ConfirmationCodeTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        del self.fields['password']
        self.fields['confirmation_code'] = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['confirmation_code'] = user.confirmation_code
        # ...
        return token


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email')
        model = User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    confirmation_code = serializers.CharField(max_length=36)

    # class Meta:
    #     fields = ('username', 'confirmation_code')
    #     model = User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name', 'confirmation_code')
        model = User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'slug']
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'slug']
        model = Genre
        lookup_field = 'slug'


class GenreRelatedField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer()
        return serializer.to_representation(value)


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(required=False, many=True, read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre', 'rating')
        model = Title

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj.id)
        n = len(reviews)
        total_score = sum([int(review.score) for review in reviews])
        if n == 0:
            return None
        return total_score/n


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    class Meta:
        exclude = ('title', )
        model = Review

    def validate(self, data):
        print('attrs', data)
        print('context', self.context.get('request'))
        method = self.context.get('request').method
        if method != "POST":
            return data
        else:
            print('22222222222', self.context.get('view').kwargs)
            title = get_object_or_404(Title, pk=self.context.get('view').kwargs.get("title_id"))
            print('author', self.context.get('request').user)
            review = Review.objects.filter(author=self.context.get('request').user, title=title)
            print('review', review)
            if review:
                print('33333333333')
                raise serializers.ValidationError('You can not leave the second review on the same title')
            return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    class Meta:
        fields = '__all__'
        model = Comment
