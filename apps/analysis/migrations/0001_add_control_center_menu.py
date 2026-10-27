"""
Migration untuk menambahkan menu "Analysis Control Center" ke database.
"""
from django.db import migrations

def add_control_center_menu(apps, schema_editor):
    Menu = apps.get_model('iam', 'Menu')
    MenuRole = apps.get_model('iam', 'MenuRole')
    Role = apps.get_model('iam', 'Role')
    
    # Cek apakah sudah ada menu dengan code yang sama
    if not Menu.objects.filter(code='analysis_control_center').exists():
        menu = Menu.objects.create(
            name='Analysis Control Center',
            code='analysis_control_center',
            icon='bi bi-terminal-fill',
            path='/analysis/control/',
            menu_type='item',
            order=1,
            is_active=True,
        )
        
        # Tambahkan MenuRole untuk semua role yang ada
        all_roles = Role.objects.filter(is_active=True)
        for role in all_roles:
            MenuRole.objects.create(menu=menu, role=role)

def remove_control_center_menu(apps, schema_editor):
    Menu = apps.get_model('iam', 'Menu')
    MenuRole = apps.get_model('iam', 'MenuRole')
    
    menus = Menu.objects.filter(code='analysis_control_center')
    MenuRole.objects.filter(menu__in=menus).delete()
    menus.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('iam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_control_center_menu, remove_control_center_menu),
    ]
