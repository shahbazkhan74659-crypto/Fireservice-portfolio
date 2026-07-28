"""Small cache-based IP/key lockout helpers, factored out of
AdminHubLoginAPIView's own inline implementation so the Forgot Password
endpoints (which need the exact same "N failures within a window" behavior)
don't duplicate it a second and third time. AdminHubLoginAPIView itself is
left untouched — it predates this module and already has test coverage
against its own inline version.

Same caveat applies here as it does there: this runs on Django's default
per-process local-memory cache (no CACHES override anywhere in this project),
so a lockout is not shared across multiple worker processes/machines in a
real multi-process production deployment.
"""

from django.core.cache import cache


def client_ip(request):
    # No reverse-proxy trust is configured anywhere in this project for
    # client-IP purposes — trusting X-Forwarded-For here would let an
    # attacker spoof a fresh IP on every request and bypass the lockout
    # entirely, so REMOTE_ADDR is used unconditionally (same reasoning as
    # AdminHubLoginAPIView._client_ip).
    return request.META.get('REMOTE_ADDR', '')


def is_locked_out(*keys, threshold):
    return any(cache.get(key, 0) >= threshold for key in keys if key)


def record_failure(key, window_seconds):
    if not key:
        return
    # add()/incr() rather than get()-then-set() to avoid losing counts to a
    # read-then-write race between concurrent requests.
    if not cache.add(key, 1, window_seconds):
        try:
            cache.incr(key)
        except ValueError:
            # Key expired between the add() and incr() calls — reseed it.
            cache.set(key, 1, window_seconds)


def clear(*keys):
    for key in keys:
        if key:
            cache.delete(key)
