from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework import routers
from .views import *
from . import views

router = routers.DefaultRouter()
router.register(r'news', views.NewsViewset)
router.register(r'articles', views.ArticlesViewset)

urlpatterns = [
    path('', cache_page(5*1)(News.as_view())),
    path('search/', cache_page(5*1)(Search.as_view())),
    path('create/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('update/<int:pk>/done', PostDetailView.as_view(), name='post_detail_before_update'),
    path('subscriber/<str:pk>/', subscribe, name='subscribe'),
    path('unsubscriber/<str:pk>/', unsubscribe, name='unsubscribe'), 
    path('', include(router.urls)),
]