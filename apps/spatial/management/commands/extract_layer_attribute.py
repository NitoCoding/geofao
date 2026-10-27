"""
Management Command untuk Ekstraksi Layer

Contoh penggunaan:

1. Ekstrak satu atribut:
   python manage.py extract_layer_attribute unit_lahan kalium K_NILAI

2. Ekstrak satu atribut dengan nama target berbeda:
   python manage.py extract_layer_attribute unit_lahan kalium K_NILAI --target-attr nilai_kalium

3. Ekstrak multiple atribut:
   python manage.py extract_layer_attribute unit_lahan karakteristik_tanah multiple --attributes K_NILAI CORG_NILAI PH_NILAI

4. List atribut dari layer:
   python manage.py extract_layer_attribute unit_lahan --list-attributes

5. Batch extraction dari config file:
   python manage.py extract_layer_attribute --batch config.json
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.spatial.utils.layer_extraction import (
    extract_layer_attribute,
    extract_multiple_attributes,
    list_layer_attributes,
    batch_extract_attributes
)
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Ekstrak atribut dari layer yang ada dan buat layer baru'

    def add_arguments(self, parser):
        parser.add_argument(
            'source_layer',
            type=str,
            help='Nama layer source (contoh: unit_lahan)'
        )

        parser.add_argument(
            'target_layer',
            type=str,
            nargs='?',
            help='Nama layer target baru (contoh: kalium)'
        )

        parser.add_argument(
            'attribute',
            type=str,
            nargs='?',
            help='Nama atribut yang diekstrak (contoh: K_NILAI) atau kata "multiple"'
        )

        parser.add_argument(
            '--target-attr',
            type=str,
            help='Nama atribut di layer target (opsional, default sama dengan source)'
        )

        parser.add_argument(
            '--attributes',
            type=str,
            nargs='+',
            help='Multiple atribut untuk diekstrak (gunakan dengan attribute="multiple")'
        )

        parser.add_argument(
            '--layer-category',
            type=str,
            default='tanah',
            choices=['tanah', 'komoditas', 'lainnya'],
            help='Kategori layer (default: tanah)'
        )

        parser.add_argument(
            '--user',
            type=str,
            help='Username yang membuat layer (opsional)'
        )

        parser.add_argument(
            '--list-attributes',
            action='store_true',
            help='List semua atribut dari layer source'
        )

        parser.add_argument(
            '--batch',
            type=str,
            help='Batch extraction dari file config JSON'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite jika target layer sudah ada (akan delete layer lama)'
        )

    def handle(self, *args, **options):
        source_layer = options['source_layer']
        target_layer = options.get('target_layer')
        attribute = options.get('attribute')

        # Mode: List Attributes
        if options['list_attributes']:
            self.list_attributes(source_layer)
            return

        # Mode: Batch Extraction
        if options['batch']:
            self.batch_extraction(options['batch'])
            return

        # Validasi required parameters
        if not target_layer or not attribute:
            self.print_help('manage.py', 'extract_layer_attribute')
            raise CommandError('Missing required arguments. Gunakan --list-attributes atau --batch untuk mode lain.')

        # Get user
        user = None
        if options.get('user'):
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                raise CommandError(f'User "{options["user"]}" tidak ditemukan')

        # Mode: Single Attribute Extraction
        if attribute != 'multiple':
            self.extract_single(source_layer, target_layer, attribute, options, user)
        # Mode: Multiple Attributes Extraction
        else:
            self.extract_multiple(source_layer, target_layer, options, user)

    def extract_single(self, source_layer, target_layer, attribute, options, user):
        """Ekstrak satu atribut"""
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'Ekstraksi Atribut Tunggal')
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'Source Layer  : {source_layer}')
        self.stdout.write(f'Target Layer  : {target_layer}')
        self.stdout.write(f'Atribut       : {attribute}')
        self.stdout.write(f'Target Attr   : {options.get("target_attr") or attribute}')
        self.stdout.write(f'{"="*60}\n')

        result = extract_layer_attribute(
            source_layer_name=source_layer,
            target_layer_name=target_layer,
            attribute_name=attribute,
            target_attribute_name=options.get('target_attr'),
            layer_category=options['layer_category'],
            user=user
        )

        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'✓ {result["message"]}'))
            self.stdout.write(f'  Target Layer ID: {result["target_layer_id"]}')
            self.stdout.write(f'  Features Extracted: {result["features_extracted"]}')
        else:
            self.stdout.write(self.style.ERROR(f'✗ {result["message"]}'))

    def extract_multiple(self, source_layer, target_layer, options, user):
        """Ekstrak multiple atribut"""
        attributes = options.get('attributes')

        if not attributes:
            raise CommandError('--attributes diperlukan untuk mode multiple')

        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'Ekstraksi Multiple Atribut')
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'Source Layer  : {source_layer}')
        self.stdout.write(f'Target Layer  : {target_layer}')
        self.stdout.write(f'Atribut       : {", ".join(attributes)}')
        self.stdout.write(f'{"="*60}\n')

        result = extract_multiple_attributes(
            source_layer_name=source_layer,
            target_layer_name=target_layer,
            attribute_names=attributes,
            layer_category=options['layer_category'],
            user=user
        )

        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'✓ {result["message"]}'))
            self.stdout.write(f'  Target Layer ID: {result["target_layer_id"]}')
            self.stdout.write(f'  Features Extracted: {result["features_extracted"]}')
            self.stdout.write(f'  Attributes: {", ".join(result["attributes_extracted"])}')
        else:
            self.stdout.write(self.style.ERROR(f'✗ {result["message"]}'))

    def list_attributes(self, layer_name):
        """List semua atribut dari layer"""
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'Atribut di Layer: {layer_name}')
        self.stdout.write(f'{"="*60}\n')

        result = list_layer_attributes(layer_name)

        if not result['success']:
            self.stdout.write(self.style.ERROR(f'✗ {result["message"]}'))
            return

        self.stdout.write(f'Total Fitur   : {result["total_features"]}')
        self.stdout.write(f'Total Atribut : {len(result["attributes"])}')
        self.stdout.write(f'\nDaftar Atribut:\n')

        for i, attr in enumerate(result['attributes'], 1):
            sample_val = result['sample_values'].get(attr, '-')
            self.stdout.write(f'  {i:2d}. {attr:20s} = {str(sample_val)[:40]}')

        self.stdout.write(f'\n{"="*60}\n')

    def batch_extraction(self, config_file):
        """Batch extraction dari file config JSON"""
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'Batch Extraction dari: {config_file}')
        self.stdout.write(f'{"="*60}\n')

        try:
            with open(config_file, 'r') as f:
                configs = json.load(f)

            if not isinstance(configs, list):
                raise ValueError('Config harus berupa list of objects')

            result = batch_extract_attributes(configs)

            self.stdout.write(f'Total Processed: {result["total_processed"]}')
            self.stdout.write(f'Successful: {len(result["successful"])}')
            self.stdout.write(f'Failed: {len(result["failed"])}')

            if result["successful"]:
                self.stdout.write(f'\n{self.style.SUCCESS("Successful Extractions:")}')
                for item in result["successful"]:
                    self.stdout.write(
                        f'  ✓ {item["config"]["source_layer"]} -> {item["config"]["target_layer"]}'
                    )

            if result["failed"]:
                self.stdout.write(f'\n{self.style.ERROR("Failed Extractions:")}')
                for item in result["failed"]:
                    self.stdout.write(
                        f'  ✗ {item["config"]["source_layer"]} -> {item["config"]["target_layer"]}'
                    )
                    self.stdout.write(f'    Error: {item["error"]}')

            self.stdout.write(f'\n{"="*60}\n')

        except FileNotFoundError:
            raise CommandError(f'File config tidak ditemukan: {config_file}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON format: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
