from django import template


register = template.Library()  # если мы не зарегистрируем наши фильтры, то Django никогда не узнает, где именно их искать, и фильтры потеряются

@register.filter(name='censor')  # регистрируем наш фильтр под именем multiply, чтоб django понимал, что это именно фильтр, а не простая функция
def censor(text):  # первый аргумент здесь — это то значение, к которому надо применить фильтр, второй аргумент — это аргумент фильтра, т. е. примерно следующее будет в шаблоне value|multiply:arg
    swearing = ['тварь', 'мразь']
    for word in swearing:
        if word in text.lower():
            raise ValueError(f'Нельзя использовать брань!')
        else:
            return text