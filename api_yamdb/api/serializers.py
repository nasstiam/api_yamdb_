from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment, User, GenreTitle


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating User model object"""
    class Meta:
        fields = ('username', 'email')
        model = User


class UserTokenSerializer(serializers.Serializer):
    """Serializer for receiving Token for User with username and Confirmation code"""
    username = serializers.CharField(max_length=50)
    confirmation_code = serializers.CharField(max_length=36)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User Model"""
    class Meta:
        fields = ('username', 'email', 'role', 'bio', 'first_name', 'last_name')
        model = User

    def validate_username(self, username):
        """Check that username is not 'me'"""
        if username == 'me':
            raise serializers.ValidationError('Username "me" is not allowed')
        return username


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        fields = ['name', 'slug']
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""
    class Meta:
        fields = ['name', 'slug']
        model = Genre
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    """Title Serializer for GET-request"""
    rating = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(required=False, many=True, read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre', 'rating')
        model = Title

    def get_rating(self, obj):
        """Calculated based on all reviews for this Title"""
        reviews = Review.objects.filter(title=obj.id)
        n = len(reviews)
        total_score = sum([int(review.score) for review in reviews])
        if n == 0:
            return None
        return total_score/n


class TitleSerializer(serializers.ModelSerializer):
    """Title Serializer for POST-request"""
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
        """Check that user can leave only one review for a title"""
        method = self.context.get('request').method
        if method != "POST":
            return data
        else:
            title = get_object_or_404(Title, pk=self.context.get('view').kwargs.get("title_id"))
            review = Review.objects.filter(author=self.context.get('request').user, title=title)
            if review:
                raise serializers.ValidationError('You can not leave the second review on the same title')
            return data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    class Meta:
        exclude = ('review', )
        model = Comment
