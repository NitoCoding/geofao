# from django.contrib import admin
from django.contrib.gis import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import *


# --- Admin untuk Model Master ---
@admin.register(MasterLayer)
class MasterLayerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "layer_type",
        "layer_category",
        "table_name",
        "data_year",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("layer_type", "layer_category", "data_year", "is_active", "created_at")
    search_fields = ("name", "table_name")
    readonly_fields = ("created_at", "updated_at")








@admin.register(LimitingFactor)
class LimitingFactorAdmin(admin.ModelAdmin):
    """
    Admin interface untuk LimitingFactor (Solusi Pengelolaan per Kelas Kesesuaian).
    """
    list_display = (
        "get_commodity",
        "get_characteristic",
        "get_suitability_class",
        "get_condition_value",
        "solution_preview",
        "get_cost_display",
        "get_priority_display",
        "time_required",
    )
    list_filter = (
        "characteristic__commodity",
        "suitability_class",
        "time_required",
        "created_at",
    )
    search_fields = (
        "solution",
        "characteristic__commodity__name",
        "characteristic__name",
    )
    readonly_fields = ("created_at", "updated_at", "get_condition_info")
    fieldsets = (
        ("Karakteristik & Kelas", {
            "fields": (
                "characteristic",
                "suitability_class",
                "get_condition_info",
            )
        }),
        ("Solusi Pengelolaan", {
            "fields": (
                "solution",
                "cost_value",
                "cost_unit",
                "time_required",
            )
        }),
        ("Metadata", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )

    def get_commodity(self, obj):
        """Tampilkan nama komoditas"""
        return obj.characteristic.commodity.name
    get_commodity.short_description = "Komoditas"
    get_commodity.admin_order_field = "characteristic__commodity__name"

    def get_characteristic(self, obj):
        """Tampilkan nama karakteristik"""
        return obj.characteristic.name
    get_characteristic.short_description = "Karakteristik"
    get_characteristic.admin_order_field = "characteristic__name"

    def get_suitability_class(self, obj):
        """Tampilkan kelas kesesuaian dengan badge warna"""
        class_colors = {
            'S1': 'green',
            'S2': 'yellow',
            'S3': 'orange',
            'N': 'red',
        }
        color = class_colors.get(obj.suitability_class, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_suitability_class_display()
        )
    get_suitability_class.short_description = "Kelas"
    get_suitability_class.allow_tags = True

    def get_condition_value(self, obj):
        """Tampilkan nilai kondisi dari SuitabilityCharacteristic"""
        return obj.get_condition_description()
    get_condition_value.short_description = "Kondisi"

    def get_condition_info(self, obj):
        """Tampilkan info kondisi di form edit"""
        condition = obj.get_condition_description()
        if condition:
            return format_html(
                '<strong>Nilai untuk kelas {}:</strong> {}',
                obj.suitability_class,
                condition
            )
        return "Kelas kesesuaian belum dipilih"
    get_condition_info.short_description = "Info Kondisi"

    def solution_preview(self, obj):
        """Tampilkan preview solusi (truncated)"""
        max_length = 50
        if len(obj.solution) > max_length:
            return obj.solution[:max_length] + "..."
        return obj.solution
    solution_preview.short_description = "Solusi"


# --- Admin untuk Data Administratif ---





@admin.register(FeatureData)
class FeatureDataAdmin(admin.GISModelAdmin):
    list_display = ("id", "layer", "get_property_count")
    list_filter = ("layer",)
    search_fields = ("layer__name",)

    def get_property_count(self, obj):
        return len(obj.attributes)

    get_property_count.short_description = "Jumlah Atribut"


# --- Admin untuk Hasil Analisis ---

@admin.register(SuitabilityAnalysisResult)
class SuitabilityAnalysisResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "commodity",
        "base_layer",
        "status",
        "analysis_method",
        "total_features",
        "s1_count",
        "s2_count",
        "s3_count",
        "n_count",
        "progress_percentage",
        "is_active",
        "created_at",
    )
    list_filter = ("status", "analysis_method", "is_active", "created_at")
    search_fields = ("commodity__name", "base_layer__name")
    readonly_fields = ("created_at", "updated_at", "started_at", "completed_at")
    fieldsets = (
        ("Relasi", {
            "fields": ("commodity", "base_layer")
        }),
        ("Status & Metode", {
            "fields": ("status", "analysis_method", "is_active", "progress_percentage")
        }),
        ("Hasil", {
            "fields": ("total_features", "s1_count", "s2_count", "s3_count", "n_count", "unknown_count")
        }),
        ("Waktu", {
            "fields": ("started_at", "completed_at", "created_at", "updated_at")
        }),
        ("Error", {
            "fields": ("error_message",),
            "classes": ("collapse",)
        }),
    )


@admin.register(SuitabilityAnalysisResultPerFeature)
class SuitabilityAnalysisResultPerFeatureAdmin(admin.ModelAdmin):
    list_display = (
        "commodity",
        "feature",
        "analysis_layer",
        "suitability_class",
        "suitability_score",
        "parent_result",
        "created_at",
    )
    list_filter = ("suitability_class", "commodity", "analysis_layer", "created_at")
    search_fields = ("commodity__name", "feature__id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ExpertReview)
class ExpertReviewAdmin(admin.ModelAdmin):
    list_display = (
        "expert",
        "get_commodity",
        "get_suitability_class",
        "notes_preview",
        "created_at",
    )
    list_filter = ("expert", "feature_result__commodity", "created_at")
    search_fields = ("expert__username", "notes", "feature_result__commodity__name")
    readonly_fields = ("created_at", "updated_at")

    def get_commodity(self, obj):
        return obj.feature_result.commodity.name
    get_commodity.short_description = "Komoditas"
    get_commodity.admin_order_field = "feature_result__commodity__name"

    def get_suitability_class(self, obj):
        return obj.feature_result.suitability_class
    get_suitability_class.short_description = "Kelas"

    def notes_preview(self, obj):
        max_len = 80
        if len(obj.notes) > max_len:
            return obj.notes[:max_len] + "..."
        return obj.notes
    notes_preview.short_description = "Catatan"
    fieldsets = (
        ("Relasi", {
            "fields": ("commodity", "feature", "analysis_layer", "parent_result")
        }),
        ("Hasil Analisis", {
            "fields": ("suitability_class", "suitability_score", "characteristic_results")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
