from uuid import uuid4

from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status, filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorModeratorAdminSuperuserOrReadOnly
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer, \
    UserCreateSerializer, UserSerializer, UserTokenSerializer, ConfirmationCodeTokenObtainPairSerializer, \
    TitleGetSerializer
from reviews.models import Category, Genre, Title, Review, Comment, User

from django.core.mail import send_mail
from django.conf import settings

# @api_view(['POST'])
# @permission_classes([AllowAny])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# def get_token(request):
#     """Receiving token for API with username and confirmation code"""
#     serializer = UserTokenSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     username = serializer.validated_data.get('username')
#     confirmation_code = serializer.validated_data.get('confirmation_code')
#     user = get_object_or_404(User, username=username)
#     if confirmation_code == user.confirmation_code:
#         print("!!!!!!!!!!!!!!!!!!!!")
#         token = AccessToken.for_user(user)
#         print(token)
#         return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
#     return Response({'confirmation_code': 'Confirmation code is not valid'},
#                     status=status.HTTP_400_BAD_REQUEST)

class UserTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserTokenSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
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

class ConfirmationCodeTokenObtainPairView(TokenObtainPairView):
    serializer_class = ConfirmationCodeTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ValueError(e)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    # serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminSuperuserOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
