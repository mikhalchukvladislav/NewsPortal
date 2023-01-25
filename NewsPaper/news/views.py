from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import date, datetime
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views import View
from django.core.paginator import Paginator
from .filters import PostFilter
from .forms import PostForm
from .models import *
from django.core.cache import cache
from django.utils import timezone
import pytz
from rest_framework import viewsets, permissions
from .serializers import *
from .models import *
import django_filters.rest_framework


class News(ListView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
    ordering = ['-created']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timezones'] = pytz.common_timezones #  добавляем в контекст все доступные часовые пояса
        context['current_time'] = timezone.localtime(timezone.now())    
        return context
 
    #  по пост-запросу будем добавлять в сессию часовой пояс, который и будет обрабатываться написанным нами ранее middleware
    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')


class Search(ListView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'news'
    ordering = ['-created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['authors'] = Author.objects.all()
        context['categories'] = list(Category.objects.values_list('pk', 'name'))
        context['user'] = User.objects.all()
        context['form'] = PostForm()
        context['pk_cat'] = self.request.GET.get('cats', None)
        context['cats'] = list(map(int, self.request.GET.getlist('cats')))
        context['is_subs'] = list(UserCategory.objects.filter(user=self.request.user).values_list('category', flat=True)) if self.request.user.is_authenticated == True else None
        context['user'] = self.request.user
        return context


def subscribe(request, **kwargs):
    category = Category.objects.get(pk=kwargs['pk'])
    cur_user = request.user
    category.subscribers.add(cur_user)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def unsubscribe(request, **kwargs):
    category = Category.objects.get(pk=kwargs['pk'])
    cur_user = request.user
    category.subscribers.remove(cur_user)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# дженерик для получения деталей о товаре
class PostDetailView(DetailView):
    template_name = 'news/certainnews.html'
    queryset = Post.objects.all()
    
    def get_object(self, *args, **kwargs): # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}', None) # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj


# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('news.add_post')
    template_name = 'news/news_create.html'
    form_class = PostForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        author_id = request.user.id
        author_name = request.user
        return render(request, self.template_name, {'form': form, 'author_id': author_id, 'author_name': author_name})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
            if Post.objects.filter(created__date=date.today()).filter(author=request.POST['author']).count() < 3:
                save = form.save()
                pk = save.id
                return redirect(f'/create/{pk}/')
            else:
                return render(request, 'news/more3posts.html')
        else:
                return render(request, 'news/more3posts.html')  


# дженерик для редактирования объекта
class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    template_name = 'news/news_update.html'
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)
    
    success_url = 'done'
 
 
# дженерик для удаления товара
class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/'


class NewsViewset(viewsets.ModelViewSet):
   queryset = Post.objects.filter(post_type='n')
   serializer_class = PostSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]
   filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
   filterset_fields = ['id']


class ArticlesViewset(viewsets.ModelViewSet):
   queryset = Post.objects.filter(post_type='a')
   serializer_class = PostSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]
   filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
   filterset_fields = ['id']


# def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса 
        
    #     if form.is_valid(): # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
    #         form.save()

    #     return super().get(request, *args, **kwargs)
        # context = {
        #     'form':form,
        #     }
        # return render(request, 'search.html', context)
        # return render(form)


    # def post(self, request, *args, **kwargs):
    #     # берём значения для нового товара из POST-запроса, отправленного на сервер

    #     author_id = request.POST['author']
    #     title = request.POST['title']
    #     text = request.POST['text']
 
    #     post = Post(author_id=author_id, title=title, text=text)  # создаём новый товар и сохраняем
    #     post.save()
    #     post.cats.add(*request.POST.getlist('cats[]'))
    #     return super().get(request, *args, **kwargs)  # отправляем пользователя обратно на GET-запрос.