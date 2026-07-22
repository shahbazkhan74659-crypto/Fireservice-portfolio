from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class ClienteleView(TemplateView):
    template_name = 'clientele.html'


class ProcessView(TemplateView):
    template_name = 'process.html'


class ServicesView(TemplateView):
    template_name = 'services.html'


class BrochureView(TemplateView):
    template_name = 'brochure.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CertificationsView(TemplateView):
    template_name = 'certifications.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SurveyPageView(TemplateView):
    template_name = 'survey.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ContactPageView(TemplateView):
    template_name = 'contact.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ConsultationView(TemplateView):
    template_name = 'consultation.html'
