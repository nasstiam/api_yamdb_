from uuid import uuid4

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status, filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorModeratorAdminSuperuserOrReadOnly, IsAdminOnly
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer, \
    UserCreateSerializer, UserSerializer, UserTokenSerializer, TitleGetSerializer
from reviews.models import Category, Genre, Title, Review, Comment, User

from django.core.mail import send_mail
from django.conf import settings


class UserTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Allow to create user, send confirmation code and obtain token"""
    queryset = User.objects.all()
    serializer_class = UserTokenSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (AllowAny,)

    def create(self, request):
        """User sends Post request with username and email and get confirmation code"""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if serializer.validated_data.get('username') == 'me':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = uuid4()
        serializer.save(confirmation_code=confirmation_code)
        subject = 'Your Confirmation Code for receiving Token'
        message = f'Your Confirmation Code is: {confirmation_code}'
        from_email = settings.EMAIL_HOST_USER
        email = request.data.get('email', '')
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            return Response(serializer.data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def create_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user:
            if confirmation_code != user.confirmation_code:
                return Response('Confirmation code is invalid',
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(str(AccessToken.for_user(user)), status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet for Model User objects"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOnly, )
    search_fields = ['username']

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=(IsAuthenticated, ),
            url_path='me',
            url_name='me'
            )
    def get_me(self, request):
        """Allows user to get detailed info about himself and edit it"""""
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user',
        permission_classes=(IsAuthenticated, IsAdminOnly)
    )
    def get_user_by_username(self, request, username):
        """Allow to get detailed users info by username"""
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Category objects"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Genre objects"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Title objects"""
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Determines which serializer will be used for different request types"""
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Review objects"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminSuperuserOrReadOnly)

    def get_queryset(self):
        """Returns queryset with reviews for specified title"""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        """Creates review on specified title, where author is current user"""
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Comment objects"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminSuperuserOrReadOnly)

    def get_queryset(self):
        """Returns queryset with comments for specified review"""
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        """Creates review on specified review, where author is current user"""
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        serializer.save(review=review, author=self.request.user)