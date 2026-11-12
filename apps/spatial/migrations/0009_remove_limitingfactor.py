"""
Migration untuk menghapus model LimitingFactor yang sudah tidak digunakan.

Data klasifikasi per karakteristik kini disimpan di
SuitabilityAnalysisResultPerFeature.characteristic_results (JSONField).
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spatial', '0008_remove_kabupaten'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LimitingFactor',
        ),
    ]