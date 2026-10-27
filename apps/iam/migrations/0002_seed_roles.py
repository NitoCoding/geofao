"""
Migration untuk seeding 3 role IAM: admin, tenaga_ahli, guest.
Superuser ditangani oleh Django built-in is_superuser.
"""
from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model('iam', 'Role')
    Menu = apps.get_model('iam', 'Menu')
    MenuRole = apps.get_model('iam', 'MenuRole')

    roles_data = [
        {
            'code': 'admin',
            'name': 'Admin',
            'description': 'Administrator sistem dengan akses penuh ke seluruh fitur aplikasi (non-Django Admin). Dapat mengelola data master, upload data spasial, menjalankan analisis, dan melihat semua hasil.',
        },
        {
            'code': 'tenaga_ahli',
            'name': 'Tenaga Ahli',
            'description': 'Tenaga ahli pertanian yang dapat mengelola data master (komoditas, kriteria), menjalankan analisis kesesuaian lahan, melihat hasil analisis, dan memberikan catatan lapangan (expert review) pada poligon hasil analisis.',
        },
    ]

    created_roles = {}
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults={
                'name': role_data['name'],
                'description': role_data['description'],
                'is_active': True,
            }
        )
        created_roles[role_data['code']] = role

    # Assign MenuRole untuk setiap role
    all_active_menus = Menu.objects.filter(is_active=True)

    for role_code, role in created_roles.items():
        if role_code == 'admin':
            # Admin: semua menu
            for menu in all_active_menus:
                MenuRole.objects.get_or_create(menu=menu, role=role)
        elif role_code == 'tenaga_ahli':
            # Tenaga Ahli: dashboard, master_data, interactive_map, analysis_results, analysis_control_center
            allowed_codes = ['dashboard', 'master_data', 'interactive_map', 'analysis_results', 'analysis_control_center']
            for menu in all_active_menus:
                if menu.code in allowed_codes:
                    MenuRole.objects.get_or_create(menu=menu, role=role)
        elif role_code == 'guest':
            # Guest: interactive_map, analysis_results (read-only)
            allowed_codes = ['interactive_map', 'analysis_results']
            for menu in all_active_menus:
                if menu.code in allowed_codes:
                    MenuRole.objects.get_or_create(menu=menu, role=role)


def remove_roles(apps, schema_editor):
    Role = apps.get_model('iam', 'Role')
    Role.objects.filter(code__in=['admin', 'tenaga_ahli', 'guest']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('iam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_roles, remove_roles),
    ]