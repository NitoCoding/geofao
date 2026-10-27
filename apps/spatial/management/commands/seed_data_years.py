from django.core.management.base import BaseCommand
from apps.spatial.models import DataYear


class Command(BaseCommand):
    help = 'Seed default data years for spatial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data years...')

        # ========== DATA YEARS ==========
        data_years = [
            {
                'year': 2024,
                'name': 'Data 2024',
                'description': 'Data spasial tahun 2024',
                'is_default': True,
                'is_active': True,
            },
        ]

        for year_data in data_years:
            year, created = DataYear.objects.get_or_create(
                year=year_data['year'],
                defaults=year_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'[+] Created: {year}'))
            else:
                # Update existing to match the defaults
                for key, value in year_data.items():
                    setattr(year, key, value)
                year.save()
                self.stdout.write(self.style.WARNING(f'[*] Updated: {year}'))

        self.stdout.write(self.style.SUCCESS(f'[+] Total data years: {DataYear.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('Seed data years completed successfully!'))
