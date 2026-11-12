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
from django_htmx.http import trigger_client_event
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.db.models import Q

from apps.spatial.models import SuitabilityAnalysisResult, SuitabilityAnalysisResultPerFeature
from apps.master_data.models import DataYear


@login_required
def results_management(request):
    """
    Halaman manajemen hasil analisis dengan 2 panel.

    Panel kiri: Daftar hasil analisis (toggle S1-S4 + fitur list).
    Panel kanan: Leaflet map dengan GeoJSON dari hasil yang aktif.
    """
    results = SuitabilityAnalysisResult.objects.select_related(
        'commodity', 'base_layer', 'created_by'
    ).order_by('-created_at').filter(status='completed')


    context = {
        'results': results,
        'data_years': DataYear.objects.filter(is_active=True).order_by('-year'),
    }

    return render(request, 'analysis/result/results_management.html', context)


@login_required
def results_panel(request):
    """
    HTMX partial: Panel kiri daftar hasil analisis.
    """
    search = request.GET.get('search', '')
    year_id = request.GET.get('year_id', '')
    page_number = request.GET.get('page', 1)

    results = SuitabilityAnalysisResult.objects.select_related(
        'commodity', 'base_layer', 'created_by'
    )

    if search:
        results = results.filter(
            Q(commodity__name__icontains=search) |
            Q(base_layer__name__icontains=search)
        )

    if year_id:
        results = results.filter(base_layer__data_year_id=year_id)

    results = results.order_by('-created_at')

    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, 'analysis/result/partials/results_panel.html', {
        'results': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })


@login_required
@require_http_methods(["POST"])
def toggle_result(request, result_id):
    """
    Toggle aktif/non-aktif untuk filter hasil yang tampil di peta.
    Setiap result bisa aktif/non-aktif secara independen.
    """
    result = get_object_or_404(SuitabilityAnalysisResult, id=result_id)
    result.is_active = not result.is_active
    result.save()

    response = HttpResponse(status=204)
    trigger_client_event(response, "resultToggled")
    trigger_client_event(response, "activeResultChanged")
    return response


@login_required
def results_geojson(request, result_id):
    """
    GeoJSON endpoint untuk hasil analisis yang aktif.
    """
    result = get_object_or_404(
        SuitabilityAnalysisResult,
        id=result_id,
        is_active=True,
        status='completed'
    )

    features = SuitabilityAnalysisResultPerFeature.objects.filter(
        commodity=result.commodity,
        analysis_layer=result.base_layer
    ).select_related('feature')

    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for f in features:
        geom = f.feature.geometry
        if geom:
            geojson['features'].append({
                'type': 'Feature',
                'geometry': json.loads(geom.geojson) if geom else None,
                'properties': {
                    'id': f.id,
                    'suitability_class': f.suitability_class,
                    'suitability_score': f.suitability_score,
                    'feature_id': f.feature.id,
                }
            })

    return JsonResponse(geojson, encoder=DjangoJSONEncoder)


def api_results_geojson(request, result_id=None):
    """
    API GeoJSON endpoint — digunakan oleh map di frontend.

    Parameters:
    - result_id: ID SuitabilityAnalysisResult (optional di query, required di path)
    """
    result_id = result_id or request.GET.get("result_id")

    if not result_id:
        return JsonResponse({"error": "result_id is required"}, status=400)

    try:
        commodity_id = request.GET.get("commodity_id")
        layer_id = request.GET.get("layer_id")

        filters = {}
        if commodity_id:
            filters["commodity_id"] = commodity_id
        if layer_id:
            filters["analysis_layer_id"] = layer_id

        if not filters:
            result = get_object_or_404(SuitabilityAnalysisResult, id=result_id)
            filters = {
                "commodity_id": result.commodity_id,
                "analysis_layer_id": result.base_layer_id,
            }

        import time
        t_start = time.perf_counter()

        rows = (
            SuitabilityAnalysisResultPerFeature.objects
            .filter(**filters)
            .annotate(geom_json=AsGeoJSON("feature__geometry", precision=6))
            .values(
                "id", "suitability_class", "suitability_score",
                "geom_json", "characteristic_results",
            )
        )

        parts = []
        for row in rows:
            props = json.dumps({
                "id": row["id"],
                "suitability_class": row["suitability_class"],
                "suitability_score": row["suitability_score"],
                "characteristic_results": row.get("characteristic_results"),
            })
            parts.append(
                '{"type":"Feature","properties":%s,"geometry":%s}'
                % (props, row["geom_json"])
            )

        body = '{"type":"FeatureCollection","features":[%s]}' % ",".join(parts)
        t_elapsed = time.perf_counter() - t_start
        logger.info(
            f"[GeoJSON-Result] result_id={result_id} "
            f"features={len(parts)} time={t_elapsed*1000:.0f}ms"
        )
        return HttpResponse(body, content_type="application/json")

    except Exception as e:
        logger.error(f"Error in api_results_geojson: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


import logging
logger = logging.getLogger(__name__)


@login_required
def result_detail(request, result_id):
    """
    HTMX partial: Detail hasil analisis untuk universal modal.
    """
    result = get_object_or_404(
        SuitabilityAnalysisResult.objects.select_related(
            'commodity', 'base_layer', 'created_by'
        ),
        id=result_id
    )
    return render(request, 'analysis/result/partials/result_detail.html', {
        'result': result,
    })
