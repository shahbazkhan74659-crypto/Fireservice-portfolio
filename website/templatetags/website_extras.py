from django import template

from website.models import ClientLogo

register = template.Library()


@register.simple_tag
def get_client_logos():
    return ClientLogo.objects.all()
