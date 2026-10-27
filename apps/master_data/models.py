from apps.core.models import BaseModel
from django.db import models


# --- Commodity & Characteristics ---
class CommodityGroup(models.Model):
    """
    Grup untuk mengelompokkan komoditas (Pangan, Hortikultura, Perkebunan, Pakan Ternak).
    """

    CATEGORY_CHOICES = [
        ("pangan", "Tanaman Pangan"),
        ("hortikultura", "Hortikultura"),
        ("perkebunan", "Perkebunan"),
        ("pakan_ternak", "Pakan Ternak"),
    ]

    name = models.CharField(max_length=50, unique=True, verbose_name="Nama Grup")
    code = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="Kode"
    )
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Tipe Kategori",
    )
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    icon = models.CharField(
        max_length=50, blank=True, verbose_name="Icon (Bootstrap Icons)"
    )
    color = models.CharField(max_length=20, blank=True, verbose_name="Warna")
    order = models.IntegerField(default=0, verbose_name="Urutan Tampilan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grup Komoditas"
        verbose_name_plural = "Grup Komoditas"
        ordering = ["order", "name"]


class Commodity(BaseModel):
    """Data master untuk komoditas pertanian."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Komoditas")
    group = models.ForeignKey(
        CommodityGroup, on_delete=models.CASCADE, verbose_name="Grup Komoditas"
    )
    suitability_table = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nama tabel hasil analisis kesesuaian untuk komoditas ini",
        verbose_name="Tabel Kesesuaian",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat pada")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Komoditas"
        verbose_name_plural = "Komoditas"

class DataYear(models.Model):
    """
    Master data untuk tahun pengumpulan data spasial.
    Setiap layer dan karakteristik lahan terhubung ke tahun tertentu.
    """
    year = models.IntegerField(unique=True, verbose_name="Tahun", help_text="Tahun pengumpulan data")
    name = models.CharField(max_length=50, blank=True, verbose_name="Nama Periode", help_text="Contoh: 'Data 2024', 'Survey 2023'")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    is_default = models.BooleanField(default=False, verbose_name="Default", help_text="Tandai sebagai tahun default")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat pada")

    def __str__(self):
        return self.name or str(self.year)

    def save(self, *args, **kwargs):
        # Jika ini di-set sebagai default, hapus flag default dari tahun lain
        if self.is_default:
            DataYear.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        # Jika ini di-set sebagai aktif, hapus flag aktif dari tahun lain
        if self.is_active:
            DataYear.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Tahun Data"
        verbose_name_plural = "Tahun Data"
        ordering = ['-year']


class LandCharacteristicCategory(models.Model):
    """
    Kategori untuk mengelompokkan karakteristik lahan.
    Contoh: Kimia Tanah, Fisika Tanah, Iklim, dll
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Kategori")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kode")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon (Bootstrap Icons)")
    color = models.CharField(max_length=20, blank=True, verbose_name="Warna")
    order = models.IntegerField(default=0, verbose_name="Urutan Tampilan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategori Karakteristik Lahan"
        verbose_name_plural = "Kategori Karakteristik Lahan"
        ordering = ['order', 'name']


class SuitabilityCharacteristic(BaseModel):
    """
    Kriteria kesesuaian untuk setiap karakteristik lahan per komoditas.

    Satu CharField per kelas (S1/S2/S3/N) yang bisa berisi:
    - **Numerik**: format range `"6.0-7.0"` atau tanda `" <4.0"`, `">9.0"`
    - **Teks**: nilai langsung `"Lempung"` atau multi-value `"Lempung, Lempung Berpasir"`

    Fungsi analisis akan mem-parse secara otomatis berdasarkan `data_type`.
    """
    DATA_TYPE_CHOICES = [
        ('numeric', 'Numerik'),
        ('text', 'Teks/Kategori'),
    ]

    commodity = models.ForeignKey(
        'master_data.Commodity',
        on_delete=models.CASCADE,
        related_name='characteristics',
        verbose_name="Komoditas"
    )
    name = models.CharField(max_length=100, verbose_name="Nama Karakteristik")
    source_field = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="Nama Field Sumber",
        help_text="Nama field di atribut shapefile/layer, misal: 'PH_NILAI', 'CORG_NILAI'"
    )
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='numeric',
        verbose_name="Tipe Data"
    )
    unit = models.CharField(max_length=20, blank=True, default='', verbose_name="Satuan")

    # --- Nilai kriteria per kelas (berfungsi untuk numerik maupun teks) ---
    # Numerik: "6.0-7.0", "<4.0", ">9.0"
    # Teks:    "Lempung", "Lempung, Lempung Berpasir"
    s1_value = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="S1 (Sangat Sesuai)",
        help_text="Numerik: '6.0-7.0' | Teks: 'Lempung'"
    )
    s2_value = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="S2 (Cukup Sesuai)",
        help_text="Numerik: '5.0-6.0' | Teks: 'Lempung Berpasir'"
    )
    s3_value = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="S3 (Sesuai Marginal)",
        help_text="Numerik: '4.0-5.0' | Teks: 'Pasir'"
    )
    n_value = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="N (Tidak Sesuai)",
        help_text="Numerik: '<4.0' atau '>9.0' | Teks: 'Bebatuan'"
    )

    def __str__(self):
        return f"{self.commodity.name} - {self.name}"

    class Meta:
        verbose_name = "Kriteria Kesesuaian"
        verbose_name_plural = "Kriteria Kesesuaian"
        unique_together = ('commodity', 'name')
