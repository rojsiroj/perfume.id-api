"""
Django command to wait for the database to be available
"""

from django.core.management.base import BaseCommand
from core.maids import db_seed


class Command(BaseCommand):
    # Django command to do initial seed

    def handle(self, *args, **kwargs):
        try:
            db_seed(True)
            self.stdout.write(
                self.style.SUCCESS("Database seeded successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding database: {e}"))
