from apps.core.models import BaseModel
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.core.validators import MinValueValidator
# from django.utils.translation import gettext_lazy as _

# ========== TAHUN DATA ==========

# ========== NOTE ==========
# Model-model karakteristik lahan (Drainase, Tekstur, Ph, dll) telah dihapus.
# Data poligon disimpan di FeatureData.attributes (JSONField).
# Tidak perlu model terpisah untuk setiap jenis karakteristik.
# ===========================

# --- Master Layer Management ---
class MasterLayer(BaseModel):
    """
    Master data untuk mengelola semua layer spasial yang diupload.
    """
    LAYER_CATEGORY_CHOICES = [
        ('tanah', 'Kandungan Tanah'),
        ('komoditas', 'Komoditas Pertanian'),
        ('base_analisis', 'Layer Dasar Analisis'),
        ('lainnya', 'Lainnya'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Layer")
    layer_type = models.CharField(
        max_length=20,
        choices=[
            ('point', 'Point'),
            ('linestring', 'LineString'),
            ('polygon', 'Polygon'),
            ('multipolygon', 'MultiPolygon'),
        ],
        verbose_name="Tipe Layer"
    )
    layer_category = models.CharField(
        max_length=20,
        choices=LAYER_CATEGORY_CHOICES,
        default='lainnya',
        blank=True,
        verbose_name="Kategori Layer",
        help_text="Kategori layer: tanah (karakteristik tanah), komoditas (pertanian), base_analisis (hasil overlay untuk input analisis FAO), atau lainnya"
    )
    table_name = models.CharField(max_length=100, unique=True, verbose_name="Nama Tabel")
    data_year = models.ForeignKey(
        'master_data.DataYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tahun Data",
        related_name="layers"
    )
    attributes = models.JSONField(default=dict, blank=True, verbose_name="Atribut")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Master Layer"
        verbose_name_plural = "Master Layers"


class FeatureData(gis_models.Model):
    """
    Menyimpan data fitur (geometri dan atribut) dari shapefile yang diupload.
    """
    layer = models.ForeignKey(
        MasterLayer, 
        on_delete=models.CASCADE, 
        related_name='features',
        verbose_name="Layer Induk"
    )
    # Gunakan JSONField untuk fleksibilitas menyimpan berbagai macam atribut
    attributes = models.JSONField(default=dict, blank=True, verbose_name="Atribut")
    geometry = gis_models.GeometryField(srid=4326, verbose_name="Geometri")

    def __str__(self):
        return f"Fitur {self.id} dari layer '{self.layer.name}'"

    class Meta:
        verbose_name = "Data Fitur"
        verbose_name_plural = "Data Fitur"

# --- Suitability Analysis Result Per Feature (Per-Polygon Cache) ---

class SuitabilityAnalysisResultPerFeature(BaseModel):
    """
    Hasil analisis kesesuaian lahan per-poligon per-komoditas.

    Tabel ini berfungsi sebagai cache hasil analisis agar tidak perlu
    menghitung ulang saat user klik poligon di peta. Satu row
    merepresentasikan hasil analisis satu komoditas pada satu fitur lahan.
    """

    FEATURE_SUITABILITY_CLASS_CHOICES = [
        ('S1', 'S1 - Sangat Sesuai'),
        ('S2', 'S2 - Cukup Sesuai'),
        ('S3', 'S3 - Sesuai Marginal'),
        ('N', 'N - Tidak Sesuai'),
        ('Unknown', 'Tidak Diketahui'),
    ]

    # Relasi
    commodity = models.ForeignKey(
        'master_data.Commodity',
        on_delete=models.CASCADE,
        related_name='per_feature_results',
        verbose_name="Komoditas"
    )
    feature = models.ForeignKey(
        FeatureData,
        on_delete=models.CASCADE,
        related_name='suitability_results',
        verbose_name="Fitur Lahan"
    )
    analysis_layer = models.ForeignKey(
        MasterLayer,
        on_delete=models.CASCADE,
        related_name='per_feature_results',
        verbose_name="Layer Analisis",
        help_text="Layer asal fitur yang dianalisis"
    )
    parent_result = models.ForeignKey(
        'spatial.SuitabilityAnalysisResult',
        on_delete=models.CASCADE,
        related_name='per_feature_results',
        null=True,
        blank=True,
        verbose_name="Hasil Analisis Induk",
        help_text="Referensi ke SuitabilityAnalysisResult (statistik agregat)"
    )

    # Hasil analisis
    suitability_class = models.CharField(
        max_length=10,
        choices=FEATURE_SUITABILITY_CLASS_CHOICES,
        default='Unknown',
        verbose_name="Kelas Kesesuaian"
    )
    suitability_score = models.FloatField(
        default=0,
        verbose_name="Skor Kesesuaian"
    )
    characteristic_results = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Hasil Per-Karakteristik",
        help_text="Detail skor setiap karakteristik lahan (opsional)"
    )

    class Meta:
        verbose_name = "Hasil Analisis Per-Poligon"
        verbose_name_plural = "Hasil Analisis Per-Poligon"
        indexes = [
            models.Index(fields=['commodity', 'analysis_layer']),
            models.Index(fields=['commodity', 'suitability_class']),
        ]
        unique_together = ['commodity', 'feature']

    def __str__(self):
        return f"{self.commodity.name} → Fitur {self.feature.id} = {self.suitability_class}"


class LimitingFactor(models.Model):
    """
    Solusi perbaikan lahan untuk setiap kelas kesesuaian yang bermasalah.
    
    Contoh:
    - Characteristic: Padi - pH Tanah
    - Class: S3
    - Solution: Pengapuran dolomit 1 ton/ha
    - Cost: 500000 Rp/ha
    """
    
    # ===== RELASI =====
    characteristic = models.ForeignKey(
        'master_data.SuitabilityCharacteristic',
        on_delete=models.CASCADE,
        related_name='limiting_factors',
        verbose_name="Karakteristik"
    )
    
    suitability_class = models.CharField(
        max_length=2,
        choices=[
            ('N', 'N - Tidak Sesuai'),
            ('S3', 'S3 - Sesuai Marginal'),
            ('S2', 'S2 - Cukup Sesuai'),
            # S1 jarang butuh solusi, tapi keep untuk fleksibilitas
            ('S1', 'S1 - Sangat Sesuai'),
        ],
        verbose_name="Kelas Kesesuaian"
    )
    
    # ===== SOLUSI =====
    solution = models.TextField(
        verbose_name="Solusi Perbaikan",
        help_text="Jelaskan langkah teknis: dosis, cara aplikasi, timing, dll."
    )
    
    # ===== BIAYA (Structured untuk Kalkulasi) =====
    cost_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Nilai Biaya",
        help_text="Angka saja (contoh: 500000 atau 500000.50)"
    )
    cost_unit = models.CharField(
        max_length=50,
        default="Rp/ha",
        verbose_name="Satuan Biaya",
        help_text="Contoh: Rp/ha, Rp/pohon, Rp/plot"
    )
    
    # ===== WAKTU (Planning) =====
    time_required = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Waktu Dibutuhkan",
        help_text="Contoh: '1-3 bulan sebelum tanam', 'Saat persiapan lahan'"
    )
    
    # ===== METADATA =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Faktor Pembatas & Solusi"
        verbose_name_plural = "Faktor Pembatas & Solusi"
        
        # ✅ PENTING: Custom ordering untuk urutan prioritas yang benar
        # Django akan sort alfabetis jika pakai field langsung,
        # jadi kita handle di view/queryset dengan annotate
        ordering = ['characteristic']
        
        # Satu karakteristik+kelas hanya boleh punya 1 solusi
        unique_together = [('characteristic', 'suitability_class')]
        
        indexes = [
            models.Index(fields=['suitability_class']),
            models.Index(fields=['characteristic', 'suitability_class']),
        ]
    
    def __str__(self):
        return f"{self.characteristic.name} ({self.suitability_class})"
    
    # ===== HELPER METHODS =====
    
    def get_priority(self):
        """
        Return prioritas berdasarkan kelas (1=tertinggi).
        N > S3 > S2 > S1
        """
        priority_map = {
            'N': 1,   # Paling urgent
            'S3': 2,
            'S2': 3,
            'S1': 4,
        }
        return priority_map.get(self.suitability_class, 99)
    
    def get_priority_display(self):
        """Return emoji + text untuk UI"""
        priority_emoji = {
            'N': '🔴 Sangat Mendesak',
            'S3': '🟠 Mendesak',
            'S2': '🟡 Perhatian',
            'S1': '🟢 Optimal',
        }
        return priority_emoji.get(self.suitability_class, '⚪ Unknown')
    
    def get_cost_display(self):
        """Format biaya untuk tampilan"""
        if self.cost_value:
            # Format dengan pemisah ribuan
            return f"Rp {self.cost_value:,.0f}/{self.cost_unit.replace('Rp/', '')}"
        return "Biaya belum tersedia"
    
    def get_commodity(self):
        """Shortcut untuk akses komoditas"""
        return self.characteristic.commodity
    
    @property
    def has_complete_info(self):
        """Check apakah data lengkap untuk ditampilkan"""
        return bool(self.solution and self.cost_value and self.time_required)


# --- Suitability Analysis Result ---
class SuitabilityAnalysisResult(BaseModel):
    """
    Hasil analisis kesesuaian lahan per-polygon.
    
    Model sederhana untuk menyimpan hasil analisis dengan metode minimum FAO.
    """
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Selesai'),
        ('failed', 'Gagal'),
    ]
    
    # Relasi
    commodity = models.ForeignKey(
        'master_data.Commodity',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='suitability_analyses',
        verbose_name="Komoditas",
        help_text="Kosong jika analisis multi-komoditas (rekomendasi)"
    )
    base_layer = models.ForeignKey(
        MasterLayer,
        on_delete=models.CASCADE,
        related_name='suitability_analyses',
        verbose_name="Layer Dasar",
        help_text="Layer yang digunakan sebagai input analisis"
    )
    
    # Status dan metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    analysis_method = models.CharField(
        max_length=20,
        default='minimum',
        verbose_name="Metode Analisis",
        help_text="Selalu menggunakan metode minimum FAO"
    )

    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Dimulai pada")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Selesai pada")
    
    # Hasil sederhana
    total_features = models.IntegerField(
        default=0,
        verbose_name="Total Fitur",
        help_text="Jumlah total polygon yang dianalisis"
    )
    s1_count = models.IntegerField(default=0, verbose_name="Jumlah S1")
    s2_count = models.IntegerField(default=0, verbose_name="Jumlah S2")
    s3_count = models.IntegerField(default=0, verbose_name="Jumlah S3")
    n_count = models.IntegerField(default=0, verbose_name="Jumlah N")
    unknown_count = models.IntegerField(default=0, verbose_name="Jumlah Unknown")
    
    # Pesan error jika gagal
    error_message = models.TextField(
        blank=True,
        verbose_name="Pesan Error"
    )
    
    # Progress tracking
    progress_percentage = models.IntegerField(
        default=0,
        verbose_name="Progress (%)"
    )
    
    def __str__(self):
        return f"{self.commodity.name} - {self.base_layer.name} ({self.status})"
    
    def get_class_distribution(self):
        """Mengembalikan distribusi kelas dalam format dictionary"""
        return {
            'S1': self.s1_count,
            'S2': self.s2_count,
            'S3': self.s3_count,
            'N': self.n_count
        }
    
    def get_total_analyzed(self):
        """Total fitur yang sudah dianalisis"""
        return self.s1_count + self.s2_count + self.s3_count + self.n_count
    
    class Meta:
        verbose_name = "Hasil Analisis Kesesuaian"
        verbose_name_plural = "Hasil Analisis Kesesuaian"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['commodity', 'created_at']),
        ]


# --- Expert Review ---

class ExpertReview(BaseModel):
    """
    Catatan/input dari tenaga ahli terhadap hasil analisis per poligon.

    Satu ahli hanya bisa memberikan satu catatan per poligon per komoditas.
    Catatan dapat diedit oleh ahli yang bersangkutan.
    """
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expert_reviews',
        verbose_name="Tenaga Ahli"
    )
    feature_result = models.ForeignKey(
        'spatial.SuitabilityAnalysisResultPerFeature',
        on_delete=models.CASCADE,
        related_name='expert_reviews',
        verbose_name="Hasil Analisis Per-Fitur"
    )
    notes = models.TextField(
        verbose_name="Catatan Lapangan",
        help_text="Observasi, rekomendasi, atau catatan kondisi lahan aktual"
    )

    def __str__(self):
        return f"Review by {self.expert.username} on {self.feature_result}"

    class Meta:
        verbose_name = "Review Tenaga Ahli"
        verbose_name_plural = "Review Tenaga Ahli"
        ordering = ['-created_at']
        unique_together = ['expert', 'feature_result']
        indexes = [
            models.Index(fields=['feature_result']),
            models.Index(fields=['expert', 'created_at']),
        ]

