from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from website.models import FireRiskAssessmentItem, MissionVisionItem, Service


class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mission_vision_items'] = MissionVisionItem.objects.all()
        return context


class ClienteleView(TemplateView):
    template_name = 'clientele.html'


class ProcessView(TemplateView):
    template_name = 'process.html'


class ServicesView(TemplateView):
    template_name = 'services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['fire_risk_items'] = FireRiskAssessmentItem.objects.all()
        return context


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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubLoginView(TemplateView):
    template_name = 'adminhub/login.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubHomeView(LoginRequiredMixin, TemplateView):
    # LoginRequiredMixin redirects to settings.LOGIN_URL ('/admin-hub/') with
    # a ?next= param when the visitor isn't authenticated. ensure_csrf_cookie
    # is needed since this page now hosts the Mission & Vision management
    # React island, which POSTs/PATCHes/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/home.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubClienteleView(LoginRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Client Logo management
    # React island, which POSTs/PATCHes/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/clientele.html'


class AdminHubCounterView(LoginRequiredMixin, TemplateView):
    # Bare placeholder, same as AdminHubHomeView originally was — no form/
    # island yet, so no ensure_csrf_cookie needed until one is added.
    template_name = 'adminhub/counter.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubServicesView(LoginRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Services and Fire Risk
    # Assessment management React islands, which POST/PATCH/DELETE with an
    # X-CSRFToken header.
    template_name = 'adminhub/services.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubCertificationsView(LoginRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Certifications
    # management React island, which POSTs/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/certifications.html'
