from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class User(AbstractUser):
    USER_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    ]
    email = models.EmailField(unique=True, blank=False,)
    username = models.CharField(max_length=50, unique=True, blank=False,)
    role = models.CharField(max_length=50, choices=USER_CHOICES,
                            default='user',)
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    year = models.IntegerField('Дата создания')
    description = models.TextField(blank=True,
                                   null=True)
    rating = models.IntegerField(blank=True,
                                 null=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="categories",
        blank=True,
        null=True
    )

    @property
    def rating(self):
        if hasattr(self, '_rating'):
            return self._rating
        return self.reviews.aggregate(Avg('score'))

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('Ревью')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10),
                                             MinValueValidator(1)])
    pub_date = models.DateTimeField(
        'Дата создания', auto_now_add=True, db_index=True
    )

    class Meta:
        unique_together = ['author', 'title']

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField('Комментарий')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата создания', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.text
