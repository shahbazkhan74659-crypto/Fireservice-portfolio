from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SurveyPageView(TemplateView):
    template_name = 'survey.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ContactPageView(TemplateView):
    template_name = 'contact.html'
