from django import template

from website.models import Brand, Certification, ClientLogo, Product, ProcessPhase, Service, SiteSetting

register = template.Library()


@register.simple_tag
def get_client_logos():
    return ClientLogo.objects.all()


@register.simple_tag
def get_brands():
    return Brand.objects.all()


@register.simple_tag
def get_products():
    return Product.objects.all()


@register.simple_tag
def get_process_phases():
    return ProcessPhase.objects.all()


@register.simple_tag
def get_services():
    return Service.objects.all()


@register.simple_tag
def get_certifications():
    return Certification.objects.all()


@register.simple_tag
def get_years_experience():
    return SiteSetting.load().years_experience


@register.simple_tag
def get_clients_served():
    return SiteSetting.load().clients_served


@register.simple_tag
def get_installations():
    return SiteSetting.load().installations


@register.simple_tag
def get_emergency_support():
    return SiteSetting.load().emergency_support


@register.simple_tag
def get_team_members():
    return SiteSetting.load().team_members
