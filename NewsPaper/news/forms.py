from django.forms import ModelForm
from .models import *
 
 
# Создаём модельную форму
class PostForm(ModelForm):
    # сheck_box = BooleanField(label='Подтвердите!')
    # в класс мета, как обычно, надо написать модель, по которой будет строиться форма и нужные нам поля. Мы уже делали что-то похожее с фильтрами.
    class Meta:
        model = Post
        fields = ['author', 'title', 'text', 'cats']