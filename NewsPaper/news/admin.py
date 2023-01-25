from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin


# @admin.register(Author)
# class AuthorAdmin(admin.ModelAdmin):
#     pass
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     pass
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     pass
# @admin.register(PostCategory)
# class PostCategoryAdmin(admin.ModelAdmin):
#     pass
# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     pass


# напишем уже знакомую нам функцию обнуления товара на складе
def nullify_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)
nullify_rating.short_description = 'Обнулить ратинг' # описание для более понятного представления в админ панеле задаётся, как будто это объект


# создаём новый класс для представления товаров в админке

class CategoryAdmin(admin.ModelAdmin):
    pass


class CategoryAdminTranslate(TranslationAdmin):
    model = Category

admin.site.register(Category, CategoryAdmin)


class AuthorAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # list_display = [field.name for field in Author._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    list_display = ('id', 'rating')
    list_filter = ('id', 'rating')
admin.site.register(Author, AuthorAdmin)


class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # list_display = [field.name for field in Author._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    list_display = ('author', 'post_type', 'created', 'title', 'text', 'rating')
    list_filter = ('author', 'post_type', 'created', 'rating')
    search_fields = ('author', 'title', 'text') # тут всё очень похоже на фильтры из запросов в базу


class PostAdminTranslate(TranslationAdmin):
    model = Post

admin.site.register(Post, PostAdmin)


class PostCategoryAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # list_display = [field.name for field in Author._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    list_display = ('post', 'category')
    list_filter = ('post', 'category')
    search_fields = ('post', 'category') # тут всё очень похоже на фильтры из запросов в базу
admin.site.register(PostCategory, PostCategoryAdmin)


class CommentAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # list_display = [field.name for field in Author._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    list_display = ('post', 'user', 'text', 'created', 'rating', 'popular')
    list_filter = ('user', 'created', 'rating')
    search_fields = ('post', 'text') # тут всё очень похоже на фильтры из запросов в базу
    actions = [nullify_rating] # добавляем действия в список
admin.site.register(Comment, CommentAdmin)
