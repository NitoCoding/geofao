"""
Views untuk halaman manajemen hasil analisis.

Layout 2-panel: kiri (list hasil + toggle) + kanan (Leaflet map).
Hanya 1 hasil analisis yang bisa aktif pada 1 waktu (radio-style).
"""

import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.db.models import Q

from apps.spatial.models import SuitabilityAnalysisResult, SuitabilityAnalysisResultPerFeature
from apps.master_data.models import DataYear


@login_required
def results_management(request):
    """
    Halaman utama manajemen hasil analisis.
    Layout 2-panel: kiri list hasil + kanan map.
    """
    results = _get_filtered_results(request)
    page_obj = _paginate_results(request, results)

    context = {
        "title": "Hasil Analisis",
        "results": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "search": request.GET.get("search", ""),
        "status_filter": request.GET.get("status", ""),
        "data_years": DataYear.objects.filter(is_active=True).order_by("-year"),
        "year": request.GET.get("year", ""),
    }
    return render(request, "analysis/results_management.html", context)


@login_required
def results_panel(request):
    """
    HTMX partial: panel kiri (list hasil + filter).
    Dipanggil saat search/filter/pagination.
    """
    results = _get_filtered_results(request)
    page_obj = _paginate_results(request, results)

    context = {
        "results": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "search": request.GET.get("search", ""),
        "status_filter": request.GET.get("status", ""),
        "year": request.GET.get("year", ""),
    }
    return render(request, "analysis/_results_panel.html", context)


@require_http_methods(["POST"])
@login_required
def toggle_result(request, result_id):
    """
    Toggle status aktif hasil analisis.
    Hanya 1 hasil yang bisa aktif — yang lain otomatis nonaktif.
    """
    result = get_object_or_404(SuitabilityAnalysisResult, id=result_id)

    if result.is_active:
        # Nonaktifkan
        result.is_active = False
        result.save(update_fields=["is_active"])
        return HttpResponse(
            '<div class="alert alert-success py-2 text-xs">Hasil dinonaktifkan</div>'
        )
    else:
        # Nonaktifkan semua hasil lain dulu
        SuitabilityAnalysisResult.objects.filter(is_active=True).update(is_active=False)
        # Aktifkan yang dipilih
        result.is_active = True
        result.save(update_fields=["is_active"])
        return HttpResponse(
            '<div class="alert alert-success py-2 text-xs">Hasil diaktifkan</div>'
        )


@login_required
def results_geojson(request, result_id):
    """
    API: kembalikan GeoJSON untuk hasil analisis tertentu.
    """
    result = get_object_or_404(SuitabilityAnalysisResult, id=result_id)

    try:
        rows = (
            SuitabilityAnalysisResultPerFeature.objects
            .filter(
                commodity_id=result.commodity_id,
                analysis_layer_id=result.base_layer_id,
            )
            .annotate(geom_json=AsGeoJSON("feature__geometry", precision=6))
            .values(
                "id",
                "feature_id",
                "suitability_class",
                "suitability_score",
                "characteristic_results",
                "feature__attributes",
                "geom_json",
            )
        )

        parts = []
        for row in rows:
            props = json.dumps(
                {
                    "per_feature_id": row["id"],
                    "feature_id": row["feature_id"],
                    "suitability_class": row["suitability_class"],
                    "suitability_score": row["suitability_score"],
                    "characteristic_results": row["characteristic_results"],
                    "feature_attributes": row["feature__attributes"],
                },
                cls=DjangoJSONEncoder,
            )
            parts.append(
                '{"type":"Feature","properties":%s,"geometry":%s}'
                % (props, row["geom_json"])
            )

        body = '{"type":"FeatureCollection","features":[%s]}' % ",".join(parts)
        return HttpResponse(body, content_type="application/json")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_filtered_results(request):
    """Filter hasil analisis berdasarkan search & status."""
    qs = SuitabilityAnalysisResult.objects.filter(
        created_by=request.user
    ).select_related("commodity", "base_layer").order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(commodity__name__icontains=search)
            | Q(base_layer__name__icontains=search)
        )

    status = request.GET.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

    year = request.GET.get("year", "").strip()
    if year:
        qs = qs.filter(base_layer__data_year__year=year)

    return qs


def _paginate_results(request, qs):
    """Paginate hasil (10 per halaman)."""
    paginator = Paginator(qs, 10)
    page_num = request.GET.get("page", 1)
    return paginator.get_page(page_num)