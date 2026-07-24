from django import template

from website.models import Brand, Certification, ClientLogo, Product, Service

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
def get_services():
    return Service.objects.all()


@register.simple_tag
def get_certifications():
    return Certification.objects.all()
