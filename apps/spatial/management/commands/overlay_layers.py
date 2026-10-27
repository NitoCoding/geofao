"""
Management Command untuk Overlay/Penggabungan Layer

Contoh penggunaan:

1. Overlay semua layer aktif:
   python manage.py overlay_layers --name "Analisis Lahan Gabungan"

2. Overlay layer spesifik:
   python manage.py overlay_layers --layers 16 18 20 --name "Layer Gabungan"

3. Overlay dengan method centroid:
   python manage.py overlay_layers --name "Overlay Centroid" --method centroid

4. Lihat statistik hasil overlay:
   python manage.py overlay_layers --stat 25
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.spatial.utils.layer_overlay import (
    overlay_layers_by_finest_resolution,
    overlay_layers_by_finest_resolution_optimized,
    get_layer_statistics
)
from apps.spatial.models import MasterLayer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Overlay/Penggabungan multiple layer berdasarkan geometry'

    def add_arguments(self, parser):
        parser.add_argument(
            '--layers',
            type=int,
            nargs='+',
            help='ID layer yang akan di-overlay (jika kosong, semua layer aktif)'
        )

        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Nama layer output hasil overlay'
        )

        parser.add_argument(
            '--table',
            type=str,
            help='Nama tabel output (default: layer_<name>)'
        )

        parser.add_argument(
            '--method',
            type=str,
            default='finest_resolution',
            choices=['intersection', 'centroid', 'grid_sampling', 'finest_resolution'],
            help='Method overlay: intersection (layer sama), centroid (point-based), grid_sampling (untuk feature count bervariasi), finest_resolution (gunakan layer terhalus sebagai base, default: finest_resolution)'
        )

        parser.add_argument(
            '--grid-size',
            type=float,
            default=0.01,
            help='Ukuran grid dalam derajat untuk method grid_sampling (default: 0.01 ~ 1km)'
        )

        parser.add_argument(
            '--user',
            type=str,
            help='Username yang menjalankan proses'
        )

        parser.add_argument(
            '--stat',
            type=int,
            help='Tampilkan statistik layer overlay hasil'
        )

        parser.add_argument(
            '--bbox',
            type=float,
            nargs=4,
            metavar=('MIN_X', 'MIN_Y', 'MAX_X', 'MAX_Y'),
            help='Filter wilayah dengan bounding box (min_x min_y max_x max_y). Contoh: --bbox 119.5 -5.0 120.0 -4.5'
        )

        parser.add_argument(
            '--wilayah',
            type=str,
            help='Filter berdasarkan field KECAMATAN. Contoh: --wilayah "Barru"'
        )

        parser.add_argument(
            '--attr-filter',
            type=str,
            nargs=2,
            metavar=('FIELD', 'VALUE'),
            help='Filter berdasarkan attribute field apa saja. Contoh: --attr-filter KECAMATAN Barru'
        )

        parser.add_argument(
            '--optimized',
            action='store_true',
            help='Gunakan fungsi optimized dengan SQL JOIN + Parallel Query (10-100x lebih cepat). Hanya untuk method finest_resolution.'
        )

        parser.add_argument(
            '--chunk-size',
            type=int,
            default=500,
            help='Ukuran chunk untuk batch processing (default: 500). Lebih kecil = lebih sering query, lebih hemat memory. Hanya untuk --optimized.'
        )

    def handle(self, *args, **options):
        # Mode: Tampilkan statistik
        if options.get('stat'):
            self.show_statistics(options['stat'])
            return

        # Mode: Overlay
        layer_name = options['name']
        layer_ids = options.get('layers')
        method = options['method']

        # Get user
        user = None
        if options.get('user'):
            try:
                User = get_user_model()
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                raise CommandError(f'User "{options["user"]}" tidak ditemukan')

        # Tentukan layer IDs
        if not layer_ids:
            # Gunakan semua layer aktif kecuali yang sudah digabungkan
            all_active = MasterLayer.objects.filter(
                is_active=True,
                layer_category='tanah'
            ).exclude(
                attributes__has_key_keys=['overlay_type']  # Exclude hasil overlay
            )

            layer_ids = list(all_active.values_list('id', flat=True))

            if not layer_ids:
                raise CommandError('Tidak ada layer aktif yang bisa di-overlay')

        # Generate table name jika tidak ditentukan
        table_name = options.get('table')
        if not table_name:
            table_name = f"layer_{layer_name.lower().replace(' ', '_')}"

        self.stdout.write(self.style.HTTP_INFO('\n' + '='*70))
        self.stdout.write(self.style.HTTP_INFO(f'OVERLAY LAYER - METHOD: {method.upper()}'))
        self.stdout.write(self.style.HTTP_INFO('='*70))

        # Tampilkan layer yang akan di-overlay
        layers = MasterLayer.objects.filter(id__in=layer_ids)
        self.stdout.write(f'\nLayer yang akan digabungkan ({layers.count()} layer):')
        for i, layer in enumerate(layers, 1):
            self.stdout.write(f'  {i}. {layer.name} (ID: {layer.id}, Table: {layer.table_name})')
            self.stdout.write(f'     Fitur: {layer.features.count()} poligon')

        self.stdout.write(f'\nOutput:')
        self.stdout.write(f'  Nama: {layer_name}')
        self.stdout.write(f'  Tabel: {table_name}')
        self.stdout.write(f'  Method: {method}')

        self.stdout.write(self.style.HTTP_INFO('\n' + '-'*70))

        # Jalankan overlay
        if method == 'finest_resolution':
            bbox = options.get('bbox')
            wilayah = options.get('wilayah')
            attr_filter = options.get('attr_filter')
            optimized = options.get('optimized', False)
            chunk_size = options.get('chunk_size', 500)

            # Build attribute filter dict
            attribute_filter = None
            if wilayah:
                # --wilayah "Barru" → filter by KECAMATAN field
                attribute_filter = {'KECAMATAN': wilayah}
            elif attr_filter:
                # --attr-filter FIELD VALUE → generic attribute filter
                field, value = attr_filter
                attribute_filter = {field: value}

            # Use optimized or original function
            if optimized:
                self.stdout.write(self.style.WARNING('\n⚡ Using OPTIMIZED function (SQL JOIN + Parallel Query)'))
                self.stdout.write(f'   Chunk size: {chunk_size}')
                self.stdout.write(f'   Parallel: Enabled\n')

                result = overlay_layers_by_finest_resolution_optimized(
                    layer_ids=layer_ids,
                    output_layer_name=layer_name,
                    output_table_name=table_name,
                    user=user,
                    bbox=bbox,
                    attribute_filter=attribute_filter,
                    chunk_size=chunk_size,
                    enable_parallel=True,
                    verbose_timing=True
                )
            else:
                result = overlay_layers_by_finest_resolution(
                    layer_ids=layer_ids,
                    output_layer_name=layer_name,
                    output_table_name=table_name,
                    user=user,
                    bbox=bbox,
                    attribute_filter=attribute_filter
                )

        # Tampilkan hasil
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS('\n✓ Overlay BERHASIL!'))
            self.stdout.write(f'\nLayer Output:')
            self.stdout.write(f'  ID: {result["output_layer_id"]}')
            self.stdout.write(f'  Nama: {result["output_layer_name"]}')
            self.stdout.write(f'  Fitur: {result["features_created"]} poligon')

            # Tampilkan performance metrics jika menggunakan optimized
            if 'performance' in result:
                perf = result['performance']
                self.stdout.write(f'\nPerformance Metrics:')
                self.stdout.write(f'  Total time: {perf["total_time_seconds"]:.2f}s')
                self.stdout.write(f'  Time per feature: {perf["time_per_feature"]:.3f}s')
                self.stdout.write(f'  Chunks processed: {perf["chunks_processed"] or "tidak tersedia"}')
                self.stdout.write(f'  Chunk size: {perf["chunk_size"] or "tidak tersedia"}')
                self.stdout.write(f'  Parallel enabled: {perf["parallel_enabled"] or "tidak tersedia"}')
                self.stdout.write(f'  Optimization: {perf["optimization_method"]}')

            # Tampilkan statistik
            stat = get_layer_statistics(result['output_layer_id'])
            if stat.get('success'):
                self.stdout.write(f'\nStatistik:')
                self.stdout.write(f'  Total fitur: {stat["total_features"]}')
                self.stdout.write(f'  Atribut per fitur: {stat["min_attributes"]} - {stat["max_attributes"]} (avg: {stat["avg_attributes"]:.1f})')

            self.stdout.write(f'\n{result["message"]}')

            # Suggestion untuk langkah selanjutnya
            self.stdout.write(self.style.HTTP_INFO('\nLangkah Selanjutnya:'))
            self.stdout.write(f'  1. Evaluasi kesesuaian: gunakan layer ID {result["output_layer_id"]} di analisis')

        else:
            self.stdout.write(self.style.ERROR(f'\n✗ Overlay GAGAL!'))
            self.stdout.write(f'Error: {result.get("message")}')

    def show_statistics(self, layer_id):
        """Tampilkan statistik layer overlay"""
        stat = get_layer_statistics(layer_id)

        if not stat.get('success'):
            self.stdout.write(self.style.ERROR(f"Error: {stat['message']}"))
            return

        layer = MasterLayer.objects.get(id=layer_id)

        self.stdout.write(self.style.HTTP_INFO('\n' + '='*70))
        self.stdout.write(self.style.HTTP_INFO(f'STATISTIK LAYER: {layer.name}'))
        self.stdout.write(self.style.HTTP_INFO('='*70))

        self.stdout.write(f'\nLayer Info:')
        self.stdout.write(f'  ID: {layer.id}')
        self.stdout.write(f'  Nama: {layer.name}')
        self.stdout.write(f'  Tabel: {layer.table_name}')
        self.stdout.write(f'  Kategori: {layer.get_layer_category_display()}')
        self.stdout.write(f'  Type: {layer.get_layer_type_display()}')

        self.stdout.write(f'\nStatistik Fitur:')
        self.stdout.write(f'  Total fitur: {stat["total_features"]}')

        self.stdout.write(f'\nStatistik Atribut:')
        self.stdout.write(f'  Min: {stat["min_attributes"]} atribut/fitur')
        self.stdout.write(f'  Max: {stat["max_attributes"]} atribut/fitur')
        self.stdout.write(f'  Avg: {stat["avg_attributes"]:.1f} atribut/fitur')

        self.stdout.write(f'\nSample Atribut ({min(20, len(stat["sample_attributes"]))} teratas):')
        for i, attr in enumerate(stat['sample_attributes'][:20], 1):
            self.stdout.write(f'  {i:2d}. {attr}')

        if len(stat['sample_attributes']) > 20:
            self.stdout.write(f'  ... dan {len(stat["sample_attributes"]) - 20} lainnya')

        # Tampilkan source layers
        attrs = layer.attributes
        if 'source_layers' in attrs:
            self.stdout.write(f'\nSource Layers:')
            for i, source_table in enumerate(attrs['source_layers'], 1):
                self.stdout.write(f'  {i}. {source_table}')
