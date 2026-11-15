from datetime import date, timedelta

from django.core.management.base import BaseCommand

from concert.models import Concert


class Command(BaseCommand):
    help = "Add two sample concerts to an empty local database."

    def handle(self, *args, **options):
        if Concert.objects.exists():
            return
        today = date.today()
        Concert.objects.bulk_create([
            Concert(concert_name="Djirection Live", city="Astana", duration=2,
                    date=today + timedelta(days=14)),
            Concert(concert_name="Night Sessions", city="Almaty", duration=3,
                    date=today + timedelta(days=42)),
        ])
        self.stdout.write(self.style.SUCCESS("Added two sample concerts."))
