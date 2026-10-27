from django.contrib import admin

from apps.master_data.models import Commodity, CommodityGroup, DataYear, LandCharacteristicCategory, SuitabilityCharacteristic

# Register your models here.
@admin.register(DataYear)
class DataYearAdmin(admin.ModelAdmin):
    list_display = ("year", "name", "is_default", "is_active", "created_at")
    list_filter = ("is_default", "is_active", "year")
    search_fields = ("year", "name", "description")
    readonly_fields = ("created_at",)
    
# --- Admin untuk Kategori Karakteristik Lahan ---
@admin.register(LandCharacteristicCategory)
class LandCharacteristicCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "order", "is_active")
    list_filter = ("is_active", "order")
    search_fields = ("name", "code", "description")

@admin.register(CommodityGroup)
class CommodityGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "suitability_table", "created_at")
    list_filter = ("group", "created_at")
    search_fields = ("name",)

@admin.register(SuitabilityCharacteristic)
class SuitabilityCharacteristicAdmin(admin.ModelAdmin):
    list_display = ("commodity", "name", "data_type", "unit")
    list_filter = ("commodity", "data_type")
    search_fields = ("commodity__name", "name")