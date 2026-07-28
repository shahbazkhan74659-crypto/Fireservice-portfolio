from django import template

register = template.Library()


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.nodelist.render(context)
        return ''


@register.tag(name='capture')
def do_capture(parser, token):
    """Renders the block between {% capture as x %} and {% endcapture %}
    into a context variable instead of directly into the page.

    Exists for exactly one reason: templates/base.html needs the rendered
    text of {% block title %}/{% block meta_description %} (already
    overridden per-page by every public template) to also populate
    og:title/og:description/twitter:title/twitter:description without
    reusing a page-specific SEO string. Django raises
    "'block' tag with name 'x' appears more than once" if the same {% block
    %} name is declared twice in one template, so the block can only be
    declared once (inside a {% capture %}) and its rendered text reused via
    the captured variable everywhere else it's needed.
    """
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise template.TemplateSyntaxError(
            "%r tag expects the format: {%% capture as varname %%}" % bits[0]
        )
    varname = bits[2]
    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, varname)
