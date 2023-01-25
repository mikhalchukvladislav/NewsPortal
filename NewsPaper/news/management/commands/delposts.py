from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category
 
 
class Command(BaseCommand):
    help = 'Команда удаляет посты той категории, которую вы укажете' # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    requires_migrations_checks = True # напоминать ли о миграциях. Если true — то будет напоминание о том, что не сделаны все миграции (если такие есть)
 
    def handle(self, *args, **options):
        # здесь можете писать любой код, который выполнится при вызове вашей команды
        categories = Category.objects.values_list('name', flat=True)
        categories_for_out = ', '.join(categories)
        self.stdout.write('Which category do you want to delete all post from? Categories: %s' % categories_for_out)
        answer1 = input('Write the category: ')

        if answer1 in categories:
            self.stdout.write('Do you really want to delete all post from some category? yes/no') # спрашиваем пользователя, действительно ли он хочет удалить все товары
            answer2 =  input() # считываем подтверждение 
            
            if answer2 == 'yes': # в случае подтверждения действительно удаляем все посты данной категории
                selected_cat = Category.objects.filter(name=answer1).values_list('id')[0]
                Post.objects.filter(cats=selected_cat).delete()
                self.stdout.write(self.style.SUCCESS('Succesfully wiped posts!'))
                return
 
        self.stdout.write(self.style.ERROR('Access denied')) # в случае неправильного подтверждения, говорим, что в доступе отказано