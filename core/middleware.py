from django.middleware.csrf import get_token


class EnsureCsrfCookieMiddleware:
    """Guarantees every response carries a CSRF cookie, site-wide.

    The public feedback widget (frontend/src/islands/feedback-widget/) is
    mounted globally via templates/base.html, so its submission form can
    POST from *any* public page — including ones with no `ensure_csrf_cookie`
    decorator or `{% csrf_token %}` tag today (e.g. AboutView, ClienteleView).
    Without this, frontend/src/lib/csrf.ts's getCsrfToken() would throw on
    those pages ("CSRF cookie not found") the first time a visitor opens the
    widget there. Calling get_token() unconditionally on every request is
    exactly what the `ensure_csrf_cookie` decorator does internally, just
    applied once here instead of decorating every public view individually
    (error-prone to keep in sync as new pages are added) or every existing
    decorated view redundantly (harmless either way).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        get_token(request)
        return self.get_response(request)
