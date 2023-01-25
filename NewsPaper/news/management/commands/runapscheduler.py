from functools import reduce
import logging
import operator
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from jinja2 import TemplateRuntimeError
from news.models import Post, Author, User, Category, UserCategory, PostCategory
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
 
 
logger = logging.getLogger(__name__)
 
 
# наша задача по выводу текста на экран
def mailing_every_week():
    category_subs = list(Category.objects.values_list('subscribers'))
    # print(category)

    for i in range(len(category_subs)):
        pk = i + 1
        posts_id = list(PostCategory.objects.filter(category_id=pk).values_list('post_id', flat=True))
        category_name = list(Category.objects.filter(pk=pk).values_list('name', flat=True))
        subs_mail = reduce(operator.concat, [list(User.objects.filter(id=i).values_list('email', flat=True)) for i in list(category_subs[i])])

        html_content = render_to_string( 
                    'mailing.html',
                    {
                        'category_name': category_name,
                        'posts_id': posts_id,
                    }
                )

        # в конструкторе уже знакомые нам параметры, да? Называются правда немного по-другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'Еженедельная рассылка новостей категории - {category_name[0]}',
            body=category_name[0],  #  это то же, что и message
            from_email='mikhalchukvladislav@yandex.ru',
            to=subs_mail,  # это то же, что и recipients_list
            # subscribers
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем
 
 
# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            mailing_every_week,
            trigger=CronTrigger(minute="*/1"),  # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")