from django.urls import path, include
from rest_framework import routers

from .views import CategoryViewSet, GenreViewSet, TitleViewSet, ReviewViewSet, CommentViewSet, \
    UserViewSet, UserTokenViewSet,  ConfirmationCodeTokenObtainPairView

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments', CommentViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', UserViewSet.as_view({'post': 'create'}), name='signup'),
    path('auth/token/', UserTokenViewSet.as_view({'post': 'create'}), name='token'),
    # path('token/refresh/', ConfirmationCodeTokenObtainPairView.as_view(), name='token_refresh')
]