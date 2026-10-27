"""
Views Sederhana untuk Analisis Kesesuaian Lahan

Menggunakan pendekatan yang mudah dipahami dengan hanya metode minimum FAO.
"""

import json
import logging

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from apps.analysis.tasks import run_simple_analysis
from apps.spatial.models import MasterLayer, SuitabilityAnalysisResult, SuitabilityAnalysisResultPerFeature
from apps.master_data.models import Commodity, CommodityGroup
from apps.analysis.analysis import analyze_suitability

logger = logging.getLogger(__name__)


@login_required
def land_suitability(request):
    """
    Halaman utama untuk analisis kesesuaian lahan.

    Menampilkan form sederhana untuk memilih:
    - Satu komoditas
    - Satu layer
    """
    context = {
        "commodity_groups": CommodityGroup.objects.filter(is_active=True),
        "commodities": Commodity.objects.select_related("group").all(),
        "layers": MasterLayer.objects.filter(
            is_active=True, layer_category="base_analisis"
        ),
    }
    return render(request, "analysis/land_suitability.html", context)


@require_http_methods(["POST"])
@login_required
def start_analysis(request):
    """
    Endpoint untuk memulai analisis kesesuaian lahan (HTMX).

    Mendukung multi-komoditas (commodity_ids[] array) dan single komoditas.
    Record hasil dibuat oleh task Celery itu sendiri.
    """
    from apps.analysis.tasks import run_multi_commodity_analysis

    commodity_ids = [c for c in request.POST.getlist("commodity_ids") if c]
    layer_id = request.POST.get("layer_id")

    if not commodity_ids or not layer_id:
        return _toast_response("Pilih minimal 1 komoditas dan 1 layer", "warning", status=400)

    try:
        commodity_ids = [int(c) for c in commodity_ids]
        layer = MasterLayer.objects.get(id=layer_id)
        commodity_names = list(
            Commodity.objects.filter(id__in=commodity_ids).values_list("name", flat=True)
        )
        if not commodity_names:
            return _toast_response("Komoditas tidak ditemukan", "error", status=404)

        if len(commodity_ids) == 1:
            run_simple_analysis.delay(
                commodity_id=commodity_ids[0],
                layer_id=layer.id,
                user_id=request.user.id,
            )
        else:
            run_multi_commodity_analysis.delay(
                commodity_ids=commodity_ids,
                layer_id=layer.id,
                user_id=request.user.id,
            )

        message = (
            f'Analisis {len(commodity_names)} komoditas ({", ".join(commodity_names)}) '
            f'pada layer "{layer.name}" telah dimulai'
        )
        response = HttpResponse(
            f'<div class="alert alert-success"><i class="bi bi-check-circle"></i>'
            f'<span>{escape(message)}. Pantau progres di tab Monitoring.</span></div>'
        )
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "success", "message": message},
            "analysisStarted": {},
            "refreshMonitoring": {},
        })
        return response

    except (ValueError, TypeError):
        return _toast_response("Format data tidak valid", "error", status=400)
    except MasterLayer.DoesNotExist:
        return _toast_response("Layer tidak ditemukan", "error", status=404)
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        return _toast_response(str(e), "error", status=500)


def _toast_response(message, toast_type, status):
    """Response kosong dengan toast via HX-Trigger (HTMX tidak me-swap respons non-2xx)."""
    response = HttpResponse(status=status)
    response["HX-Trigger"] = json.dumps({
        "showToast": {"type": toast_type, "message": message}
    })
    return response


@login_required
def check_status(request, result_id):
    """
    Cek status analisis.
    """
    result = get_object_or_404(SuitabilityAnalysisResult, id=result_id)

    if request.headers.get("HX-Request"):
        # HTMX request: kembalikan HTML partial
        return render(request, "analysis/partials/status.html", {"result": result})
    else:
        # API request: kembalikan JSON
        return JsonResponse(
            {
                "status": result.status,
                "progress": result.progress_percentage,
                "total_features": result.total_features,
                "s1_count": result.s1_count,
                "s2_count": result.s2_count,
                "s3_count": result.s3_count,
                "n_count": result.n_count,
                "created_at": result.created_at,
                "completed_at": result.completed_at,
            }
        )


@login_required
def quick_analysis(request):
    """
    Analisis cepat dengan input data tanah manual.

    User bisa input data tanah langsung di form.
    """
    if request.method == "POST":
        commodity_id = request.POST.get("commodity_id")
        # Ambil data tanah dari form
        soil_data = {}

        # Contoh field yang mungkin ada
        fields = ["pH Tanah", "C-Organik", "Tekstur", "Kemiringan Lereng"]
        for field in fields:
            value = request.POST.get(field)
            if value:
                soil_data[field] = value

        if not commodity_id or not soil_data:
            return HttpResponse(
                '<div class="alert alert-error">Data tidak lengkap</div>', status=400
            )

        # Jalankan analisis
        result = analyze_suitability(int(commodity_id), soil_data)

        # Tampilkan hasil
        return render(
            request, "analysis/partials/quick_result.html", {"result": result}
        )

    # GET request: tampilkan form
    context = {"commodities": Commodity.objects.all()}
    return render(request, "analysis/quick_analysis.html", context)


@login_required
def analysis_results(request):
    """
    Halaman untuk melihat semua hasil analisis.
    """
    results = SuitabilityAnalysisResult.objects.filter(
        created_by=request.user
    ).order_by("-created_at")

    return render(request, "analysis/results.html", {"results": results})
import json
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.db.models.functions import AsGeoJSON

def api_results_geojson(request, result_id=None):
    if result_id:
        try:
            parent = SuitabilityAnalysisResult.objects.get(id=result_id)
            commodity_id = parent.commodity_id
            layer_id = parent.base_layer_id
        except SuitabilityAnalysisResult.DoesNotExist:
            return JsonResponse(
                {"error": "Hasil analisis tidak ditemukan"}, status=404
            )
    else:
        commodity_id = request.GET.get("commodity_id")
        layer_id = request.GET.get("layer_id")

        if not commodity_id or not layer_id:
            return JsonResponse(
                {"error": "commodity_id dan layer_id wajib diisi"}, status=400
            )

    try:
        rows = (
            SuitabilityAnalysisResultPerFeature.objects
            .filter(commodity_id=commodity_id, analysis_layer_id=layer_id)
            # precision=6 cukup untuk lat/lon, mengurangi ukuran payload
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

        # Bangun string JSON langsung, tanpa parse-ulang geometry
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