from api.filters import TitleFilter
from api.permissions import (AdminOrReadonly, IsAdminorUpdateReadOnly,
                             IsAuthorAdminModeratorOrReadOnly)
from django.conf import settings
# from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import filters as f
from rest_framework import mixins, response, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTitleSerializer,
                          GetTokenSerializer, PostTitleSerializer,
                          ReviewSerializer, TokenSerializer, UpdateSerializer,
                          UserSerializer)

# User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Для Usera"""
    permission_classes = (IsAdminorUpdateReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_serializer_class(self):
        """Выбор сериализатора"""

        if self.request.user.is_admin:
            if self.request.method == "PATCH":
                return UserSerializer
            if self.request.method == "POST":
                return UserSerializer
            return UpdateSerializer
        return UpdateSerializer

    def destroy(self, request, username, **kwargs):
        username = self.kwargs['username']
        if username != 'me':
            if self.request.user.is_admin:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise Http404
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            if self.request.user.is_user or self.request.user.is_moderator:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        """Если вы администратор, возвращает список пользователей"""

        if self.request.user.is_admin:
            return User.objects.all()
        raise PermissionDenied("Вы не администратор!")

    def get_object(self):
        """Дает пользователя в зависимости от юзернейма в url"""
        return super().get_object()

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user, many=False)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = UpdateSerializer(
                instance=request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def me_is_user(self, request):
        """Выбор сериализатора в зависимости от метода и пользователя"""

        serializer = self.get_serializer_class()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create(request):
    """Отправляет специальный код на email."""

    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.data['username']
    if user == 'me':
        return response.Response(serializer.errors,
                                 status=status.HTTP_400_BAD_REQUEST)
    email = serializer.data['email']

    user_new, created = User.objects.get_or_create(email=email,
                                                   username=user)
    confirmation_code = default_token_generator.make_token(user_new)
    message = confirmation_code
    subject = "Подтвердите свой профиль, введя код из письма"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], )
    return response.Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def token(request):
    """Дает токен по коду из email, проверка правильности пары юзернейм-код"""

    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_s = serializer.data['username']
    confirmation_code = serializer.data['confirmation_code']
    user = get_object_or_404(User, username=user_s)
    if not default_token_generator.check_token(user, confirmation_code):
        return response.Response(serializer.errors,
                                 status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    new_token = GetTokenSerializer(data={'token': str(refresh.access_token)})
    new_token.is_valid(raise_exception=True)
    return response.Response(new_token.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Для тайтла"""

    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AdminOrReadonly,)
    filterset_fields = ('name', 'year', 'category', 'genre', )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Выбор сериализатора"""

        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return PostTitleSerializer
        return GetTitleSerializer

    def get_queryset(self):
        return Title.objects.all().annotate(_rating=Avg('reviews__score'))


class ReviewViewSet(viewsets.ModelViewSet):
    """Для ревью"""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def create(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Review.objects.filter(author=self.request.user,
                                 title=self.get_title()).exists():
            content = {'field_name': 'такое ревью уже существует'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied()
        serializer.save()


class GetCreateDestroyMixin(mixins.CreateModelMixin,
                            mixins.ListModelMixin, mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    pass


class GenreViewSet(GetCreateDestroyMixin):
    """Для жанра"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOrReadonly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CommentViewSet(viewsets.ModelViewSet):
    """Для комментов"""

    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):

        review = get_object_or_404(Review,
                                   id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review,
                                   id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        author = get_object_or_404(User, username=self.request.user.username)

        serializer.save(author=author, review=review)


class CategoryViewSet(GetCreateDestroyMixin):
    """Для категорий"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOrReadonly,)
    filter_backends = (f.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_fields = ('slug',)
