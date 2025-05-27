# core/signals.py
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

logger = logging.getLogger(__name__)  # use your app name here


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info(f'User logged in: {user.name} - {user.crm} (IP: {get_client_ip(request)})')


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    logger.info(f'User logged out: {user.name} - {user.crm} (IP: {get_client_ip(request)})')


def get_client_ip(request):
    return request.META.get('REMOTE_ADDR', 'unknown')
