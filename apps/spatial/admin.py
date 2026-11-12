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
