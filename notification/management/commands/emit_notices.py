from django.core.management.base import NoArgsCommand

from notification.engine import send_all

class Command(NoArgsCommand):
    help = "Emit queued notices."

    def handle_noargs(self, **options):
        send_all()
