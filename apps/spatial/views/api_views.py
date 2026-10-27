"""
Category API Views

Handles API endpoints for categories:
- Land characteristic categories
- Commodity categories
- Commodities by category
"""
import logging

from django.http import JsonResponse

from apps.master_data.models import (
    Commodity,
    CommodityGroup,
    LandCharacteristicCategory,
)

logger = logging.getLogger(__name__)


# ========== API ENDPOINTS FOR CATEGORIES ==========

def api_land_categories(request):
    """
    API endpoint untuk mendapatkan semua kategori karakteristik lahan.
    Returns JSON dengan struktur: {code, name, icon, color, order}
    """

    categories = LandCharacteristicCategory.objects.filter(is_active=True).order_by(
        "order", "name"
    )

    data = [
        {
            "id": cat.id,
            "code": cat.code,
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "color": cat.color,
            "order": cat.order,
        }
        for cat in categories
    ]

    return JsonResponse({"categories": data}, safe=False)


def api_commodity_categories(request):
    """
    API endpoint untuk mendapatkan semua kategori komoditas.
    Returns JSON dengan struktur: {code, name, category_type, icon, color}
    """
    categories = CommodityGroup.objects.filter(is_active=True).order_by("order", "name")

    data = [
        {
            "id": cat.id,
            "code": cat.code,
            "name": cat.name,
            "category_type": cat.category_type,
            "description": cat.description,
            "icon": cat.icon,
            "color": cat.color,
            "order": cat.order,
        }
        for cat in categories
    ]

    return JsonResponse({"categories": data}, safe=False)


def api_commodities_by_category(request, category_type):
    """
    API endpoint untuk mendapatkan komoditas berdasarkan kategori.
    category_type: pangan, hortikultura, perkebunan, pakan_ternak

    Returns JSON dengan daftar komoditas dalam kategori tersebut.
    """
    try:
        commodity_groups = CommodityGroup.objects.filter(
            category_type=category_type, is_active=True
        ).order_by("order", "name")

        commodities = (
            Commodity.objects.filter(group__in=commodity_groups)
            .select_related("group")
            .order_by("name")
        )

        data = [
            {
                "id": com.id,
                "name": com.name,
                "group": com.group.name,
                "group_code": com.group.code,
                "suitability_table": com.suitability_table,
            }
            for com in commodities
        ]

        return JsonResponse(
            {"category_type": category_type, "commodities": data}, safe=False
        )

    except Exception as e:
        logger.error(f"Error fetching commodities by category: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
