from django.core.management.base import BaseCommand

from user_requests.services import close_expired_requests


class Command(BaseCommand):
    help = "Expires pending user requests less than 24 hours from their shift."

    def handle(self, *args, **options):
        expired_count = close_expired_requests()

        self.stdout.write(
            self.style.SUCCESS(
                f"Expired {expired_count} user request(s)."
            )
        )