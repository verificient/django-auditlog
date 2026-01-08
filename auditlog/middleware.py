import contextlib
import threading
import time
from functools import partial

from django.apps import apps
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.deprecation import MiddlewareMixin

from auditlog.context import set_actor
from auditlog.models import LogEntry

threadlocal = threading.local()

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


def get_current_request():
    """returns the request object for this thread"""
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """returns the current user, if exist, otherwise returns None"""
    request = get_current_request()
    if request:
        return getattr(request, "user", None)


class AuditlogMiddleware:
    """
    Middleware to couple the request's user to log items. This is accomplished by currying the
    signal receiver with the user from the request (or None if the user is not authenticated).
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    @staticmethod
    def _get_remote_addr(request):
        # In case there is no proxy, return the original address
        if not request.headers.get("X-Forwarded-For"):
            return request.META.get("REMOTE_ADDR")

        # In case of proxy, set 'original' address
        remote_addr: str = request.headers.get("X-Forwarded-For").split(",")[0]

        # Remove port number from remote_addr
        if "." in remote_addr and ":" in remote_addr:  # IPv4 with port (`x.x.x.x:x`)
            remote_addr = remote_addr.split(":")[0]
        elif "[" in remote_addr:  # IPv6 with port (`[:::]:x`)
            remote_addr = remote_addr[1:].split("]")[0]

        return remote_addr

    def __call__(self, request):
        remote_addr = self._get_remote_addr(request)

        if hasattr(request, "user") and request.user.is_authenticated:
            context = set_actor(actor=request.user, remote_addr=remote_addr)
        else:
            context = contextlib.nullcontext()

        with context:
            return self.get_response(request)


class ThreadLocalMiddleware(MiddlewareMixin):
    """ Simple middleware that adds the request object in thread local stor    age."""

    def process_request(self, request):
        _thread_locals.request = request

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response
