from django.core.management.base import BaseCommand
from apps.spatial.models import LandCharacteristicCategory, CommodityGroup


class Command(BaseCommand):
    help = 'Seed default data for land characteristic and commodity categories'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')

        # ========== KATEGORI KARAKTERISTIK LAHAN ==========
        land_categories_data = [
            {
                'code': 'kimia_tanah',
                'name': 'Kimia Tanah',
                'description': 'Karakteristik kimia tanah seperti pH, KTK, Kalium, dll',
                'icon': 'bi bi-droplet-fill',
                'color': '#e74c3c',
                'order': 1,
            },
            {
                'code': 'fisika_tanah',
                'name': 'Fisika Tanah',
                'description': 'Karakteristik fisika tanah seperti tekstur, bulk density, dll',
                'icon': 'bi bi-layers-fill',
                'color': '#3498db',
                'order': 2,
            },
            {
                'code': 'iklim',
                'name': 'Iklim & Curah Hujan',
                'description': 'Data iklim dan curah hujan',
                'icon': 'bi bi-cloud-rain-fill',
                'color': '#9b59b6',
                'order': 3,
            },
            {
                'code': 'topografi',
                'name': 'Topografi',
                'description': 'Karakteristik topografi seperti kemiringan lereng, kedalaman tanah',
                'icon': 'bi bi-geo-alt-fill',
                'color': '#27ae60',
                'order': 4,
            },
        ]

        for cat_data in land_categories_data:
            LandCharacteristicCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(land_categories_data)} land characteristic categories'))

        # ========== KATEGORI KOMODITAS ==========
        commodity_groups_data = [
            # Tanaman Pangan
            {
                'code': 'padi',
                'name': 'Padi',
                'category_type': 'pangan',
                'description': 'Berbagai varietas padi',
                'icon': 'bi bi-basket-fill',
                'color': '#f39c12',
                'order': 1,
            },
            {
                'code': 'jagung',
                'name': 'Jagung',
                'category_type': 'pangan',
                'description': 'Berbagai varietas jagung',
                'icon': 'bi bi-basket-fill',
                'color': '#f1c40f',
                'order': 2,
            },
            {
                'code': 'kedelai',
                'name': 'Kedelai',
                'category_type': 'pangan',
                'description': 'Berbagai varietas kedelai',
                'icon': 'bi bi-basket-fill',
                'color': '#e67e22',
                'order': 3,
            },
            # Hortikultura
            {
                'code': 'cabai',
                'name': 'Cabai',
                'category_type': 'hortikultura',
                'description': 'Berbagai jenis cabai',
                'icon': 'bi bi-flower1',
                'color': '#e74c3c',
                'order': 10,
            },
            {
                'code': 'tomat',
                'name': 'Tomat',
                'category_type': 'hortikultura',
                'description': 'Berbagai jenis tomat',
                'icon': 'bi bi-flower1',
                'color': '#c0392b',
                'order': 11,
            },
            {
                'code': 'kentang',
                'name': 'Kentang',
                'category_type': 'hortikultura',
                'description': 'Berbagai varietas kentang',
                'icon': 'bi bi-flower1',
                'color': '#f39c12',
                'order': 12,
            },
            {
                'code': 'sayuran',
                'name': 'Sayuran Daun',
                'category_type': 'hortikultura',
                'description': 'Bayam, kangkung, dll',
                'icon': 'bi bi-flower1',
                'color': '#27ae60',
                'order': 13,
            },
            # Perkebunan
            {
                'code': 'kopi',
                'name': 'Kopi',
                'category_type': 'perkebunan',
                'description': 'Arabika, Robusta, dll',
                'icon': 'bi bi-tree-fill',
                'color': '#8b4513',
                'order': 20,
            },
            {
                'code': 'teh',
                'name': 'Teh',
                'category_type': 'perkebunan',
                'description': 'Berbagai varietas teh',
                'icon': 'bi bi-tree-fill',
                'color': '#27ae60',
                'order': 21,
            },
            {
                'code': 'kakao',
                'name': 'Kakao',
                'category_type': 'perkebunan',
                'description': 'Berbagai varietas kakao',
                'icon': 'bi bi-tree-fill',
                'color': '#6d4c41',
                'order': 22,
            },
            {
                'code': 'kelapa',
                'name': 'Kelapa',
                'category_type': 'perkebunan',
                'description': 'Kelapa dalam, genjah, dll',
                'icon': 'bi bi-tree-fill',
                'color': '#16a085',
                'order': 23,
            },
            # Pakan Ternak
            {
                'code': 'rumput_gajah',
                'name': 'Rumput Gajah',
                'category_type': 'pakan_ternak',
                'description': 'Rumput gajah dan varietasnya',
                'icon': 'bi bi-grid-fill',
                'color': '#27ae60',
                'order': 30,
            },
            {
                'code': 'rumput_laut',
                'name': 'Rumput Laut/Other',
                'category_type': 'pakan_ternak',
                'description': 'Rumput laut dan pakan lainnya',
                'icon': 'bi bi-grid-fill',
                'color': '#16a085',
                'order': 31,
            },
            {
                'code': 'legum',
                'name': 'Legum Pakan Ternak',
                'category_type': 'pakan_ternak',
                'description': 'Lamtoro, kudzu, dll',
                'icon': 'bi bi-grid-fill',
                'color': '#f39c12',
                'order': 32,
            },
        ]

        for group_data in commodity_groups_data:
            CommodityGroup.objects.get_or_create(
                code=group_data['code'],
                defaults=group_data
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(commodity_groups_data)} commodity groups'))
        self.stdout.write(self.style.SUCCESS('Seed data completed successfully!'))
