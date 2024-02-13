from django.views.generic import TemplateView
from django.shortcuts import render


class AboutPage(TemplateView):
    """Класс представления страницы о проекте."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Класс представления страницы с правилами."""

    template_name = 'pages/rules.html'


# 3 FBV для кастомных страниц с ошибками

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def error_view(request, template='pages/500.html'):
    return render(request, template, status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
