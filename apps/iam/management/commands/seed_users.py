"""
Management command untuk inject dummy users.

Usage:
    python manage.py seed_users [--count 20]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from apps.iam.models import User


class Command(BaseCommand):
    help = "Inject dummy users untuk testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Jumlah dummy user yang akan dibuat (default: 20)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        password = make_password("password")
        created = 0

        for i in range(1, count + 1):
            username = f"dummy{i:02d}"
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"  ⏭  {username} sudah ada, skip"))
                continue

            User.objects.create(
                username=username,
                email=f"dummy{i:02d}@example.com",
                password=password,
                first_name=f"Dummy",
                last_name=f"User {i:02d}",
                is_active=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f"  ✓ {username} created"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ {created} dummy user berhasil dibuat."))