# from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import ManyRelatedField, SlugRelatedField
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User

# User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Для юзера пост-запросов"""

    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())])

    username = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())])

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UpdateSerializer(serializers.ModelSerializer):
    """Для юзера patch запросов"""

    class Meta:
        fields = ('username',
                  'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)
        model = User


class TokenSerializer(serializers.Serializer):
    """Для создания ввода 1 токена, который получен по email"""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class GetTokenSerializer(serializers.Serializer):
    """Для получения итогового токена"""
    token = serializers.CharField(required=True)


class GenreSerializer(serializers.ModelSerializer):
    """Для жанров"""

    class Meta:
        exclude = ('id', )
        model = Genre
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CommentSerializer(serializers.ModelSerializer):
    """Для комментариев"""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        depth = 1
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    """Для категорий"""

    class Meta:
        depth = 1
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategoryRelatedField(serializers.SlugRelatedField):
    """Для правильной выдачи результата после пост запроса для тайтла"""

    def to_representation(self, value):
        return CategorySerializer(value).data


class GenreRelatedField(serializers.SlugRelatedField):
    """Для правильной выдачи результата после пост запроса для тайтла"""

    def to_representation(self, value):
        return GenreSerializer(value).data


class GetTitleSerializer(serializers.ModelSerializer):
    """Для гет-запросов тайтлов"""

    category = CategorySerializer()
    genre = ManyRelatedField(child_relation=GenreSerializer())
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        fields = '__all__'
        model = Title


class PostTitleSerializer(serializers.ModelSerializer):
    """Для пост запросов тайтлов"""

    genre = GenreRelatedField(slug_field='slug',
                              queryset=Genre.objects.all(), many=True)
    category = CategoryRelatedField(slug_field='slug',
                                    queryset=Category.objects.all())

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'rating',
                  'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Для ревью"""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('title',)
        extra_kwargs = {'text': {'required': True},
                        'score': {'required': True}}

        def validate(self, data):
            """Валидация на дублирование отзыва"""

            reviews = data.get('author').reviews.all()
            if reviews.objects.get(id=data.get('id')).exists():
                raise serializers.ValidationError(
                    'Создавать можно только 1 отзыв.'
                )
            return data
