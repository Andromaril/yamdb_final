from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, create, token)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet, basename='title')
router.register('categories', CategoryViewSet)
router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment')
router.register(r'^titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='comment')


urlpatterns_users = [
    path('token/', token, name='token_obtain_pair'),
    path('signup/', create, name='create_code'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(urlpatterns_users)),
]
