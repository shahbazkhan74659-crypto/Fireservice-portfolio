from django import template

from website.models import Brand, ClientLogo

register = template.Library()


@register.simple_tag
def get_client_logos():
    return ClientLogo.objects.all()


@register.simple_tag
def get_brands():
    return Brand.objects.all()
