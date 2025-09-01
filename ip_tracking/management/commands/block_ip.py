from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Block an IP address by adding it to the BlockedIP table."

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="The IP address to block")

    def handle(self, *args, **kwargs):
        ip = kwargs["ip_address"]
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully blocked IP: {ip}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP {ip} is already blocked."))
