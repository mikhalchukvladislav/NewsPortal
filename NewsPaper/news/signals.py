from functools import reduce
from django.dispatch import receiver # импортируем нужный декоратор
from news.models import Post, User, Category
import operator
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.db.models.signals import m2m_changed
from news.tasks import mailing
 
# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(m2m_changed, sender=Post.cats.through)
def notify_managers_appointment(sender, action, instance, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            subs = [list(User.objects.filter(pk=i).values_list('email',flat=True)) for i in list(Category.objects.filter(pk=pk).values_list('subscribers', flat=True))]
            subscribers = reduce(operator.concat, subs)
            category = Category.objects.filter(pk=pk).values_list('name', flat=True)[0]
            text = instance.text
            author = instance.author
            # получаем наш html
            
            html_content = render_to_string( 
                'mail.html',
                {
                    'new_post_text': text,
                    'new_post_author': author,
                }
            )
             
            mailing.delay(category, text, subscribers, html_content)
