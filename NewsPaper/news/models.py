from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.cache import cache


class Author(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    rating = models.IntegerField(default = 0)

    def update_rating(self, new_rating):
        self.rating = new_rating
        self.save()
    
    def __str__(self):
        return f'{self.user.username}'


class Category(models.Model):
    name = models.CharField(max_length = 64, unique = True)
    subscribers = models.ManyToManyField(User, through='UserCategory')

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    article = 'a'
    news = 'n'

    POST_TYPE = [
        (article, "Статья"),
        (news, "Новость")
    ]

    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    post_type = models.CharField(max_length = 1, choices = POST_TYPE, default = article)
    created = models.DateTimeField(auto_now_add = True)
    cats = models.ManyToManyField(Category, through = 'PostCategory')
    title = models.CharField(max_length = 256)
    text = models.TextField()
    rating = models.IntegerField(default = 0, validators=[MinValueValidator(0, 'Рейтинг не может быть меньше 0')])
    
    def like(self):
        self.rating += 1
        self.save()
        
    def dislike(self):
        self.rating -= 1
        self.save()
        
    def preview(self):
        size = 124 if len(self.text) > 124 else len(self.text)
        return self.text[:size]+'...'
    
    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}') # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default = 0)

    # допишем свойство, которое будет отображать, есть ли товар на складе
    @property
    def popular(self):
        return self.rating > 0
    
    def like(self):
        self.rating += 1
        self.save()
        
    def dislike(self):
        self.rating -= 1
        self.save()


class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)