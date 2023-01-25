from django_filters import FilterSet, DateFilter, CharFilter  # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import Post
from django.forms import SelectDateWidget
 
 
# создаём фильтр
class PostFilter(FilterSet):
    created = DateFilter(field_name='created',
                               lookup_expr='gt',
                               label='Дата',
                               widget=SelectDateWidget)
    title = CharFilter(label='Заголовок', lookup_expr='icontains')
    author = CharFilter(label='Автор', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = (
            'title',
            'created',
            'author',
            'cats',) # поля, которые мы будем фильтровать (т. е. отбирать по каким-то критериям, имена берутся из моделей)
        # fields = {
        #         'name': ['icontains'],  # мы хотим чтобы нам выводило имя хотя бы отдалённо похожее на то, что запросил пользователь
        #         'quantity': ['gt'],  # количество товаров должно быть больше или равно тому, что указал пользователь
        #         'price': ['lt'],  # цена должна быть меньше или равна тому, что указал пользователь
        #         }