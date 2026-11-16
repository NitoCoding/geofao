"""
Map and GeoJSON Views

Handles map display and GeoJSON API endpoints:
- Map view
- GeoJSON layer API
- Feature at point query
"""
import json
import logging

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse

from helpers import translate_soil_param
from apps.master_data.models import Commodity, DataYear
from apps.spatial.models import MasterLayer, FeatureData, SuitabilityAnalysisResult, SuitabilityAnalysisResultPerFeature, ExpertReview

logger = logging.getLogger(__name__)


# ========== MAP VIEW ==========

def map_view(request):
    """
    Tampilan peta interaktif (rework).
    Menampilkan layer dan hasil analisis dengan status aktif saja (is_active=True)
    dalam dua tab terpisah: Layer Aktif & Hasil Analisis Aktif.
    Note: Map page requires full page load due to Leaflet JS initialization.
    HTMX partial loading is not recommended for this page.
    """
    active_layers = MasterLayer.objects.filter(
        is_active=True,
        data_year__is_active=True,
    ).select_related('data_year')
    active_results = SuitabilityAnalysisResult.objects.filter(
        is_active=True,
        status='completed',
        base_layer__data_year__is_active=True,
    ).select_related('commodity', 'base_layer').order_by('-created_at')
    context = {
        "active_layers": active_layers,
        "active_results": active_results,
        "title": "Peta Aktif",
        "is_admin": request.user.is_authenticated and (
            request.user.is_superuser or request.user.has_role("admin")
        ),
    }

    # Always return full page for map (Leaflet needs full page load)
    return render(request, "spatial/map_rework.html", context)


# ========== GEOJSON API ==========

def api_layer_geojson(request, pk):
    """
    API endpoint untuk mengembalikan data sebuah layer dalam format GeoJSON.

    Menggunakan string_agg + ST_AsGeoJSON(geom, 6) + HttpResponse untuk menghindari
    double serialization dan memperkecil ukuran payload (precision 6 desimal ≈ 11cm).
    """
    import time
    from django.db import connection

    t_start = time.perf_counter()

    try:
        layer = MasterLayer.objects.get(pk=pk)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(string_agg(
                    '{"type":"Feature","properties":' || attributes::text
                    || ',"geometry":' || ST_AsGeoJSON(geometry, 6) || '}'
                , ','), '')
                FROM spatial_featuredata
                WHERE layer_id = %s
            """, [pk])
            features_str = cursor.fetchone()[0] or ''

        t_query = time.perf_counter()

        body = '{"type":"FeatureCollection","features":[%s]}' % features_str
        t_total = time.perf_counter() - t_start
        t_db = t_query - t_start

        feature_count = features_str.count('"type":"Feature"') if features_str else 0
        logger.info(
            f"[GeoJSON] layer_id={pk} name='{layer.name}' "
            f"features={feature_count} "
            f"db={t_db*1000:.1f}ms total={t_total*1000:.1f}ms"
        )
        return HttpResponse(body, content_type="application/json")

    except MasterLayer.DoesNotExist:
        logger.error(f"Layer with pk={pk} not found.")
        return JsonResponse({"error": "Layer not found"}, status=404)
    except Exception as e:
        logger.error(
            f"Error generating GeoJSON for layer pk={pk}: {str(e)}", exc_info=True
        )
        return JsonResponse({"error": "An internal server error occurred."}, status=500)


# ========== FEATURE AT POINT API ==========

def api_feature_at_point(request):
    """
    API endpoint untuk mendapatkan fitur pada titik tertentu menggunakan ST_Intersects.

    Query parameters:
    - layer_id: ID layer MasterLayer
    - lng: Longitude titik klik
    - lat: Latitude titik klik

    Returns:
    JSON dengan format:
    - Success: {id, properties, type, geometry}
    - No data: {info: 'message'}
    - Error: {error: 'message', details: 'details'}
    """
    from django.contrib.gis.geos import Point

    layer_id = request.GET.get("layer_id")
    lng = request.GET.get("lng")
    lat = request.GET.get("lat")

    # Validasi parameter
    if not all([layer_id, lng, lat]):
        return JsonResponse(
            {
                "error": "Missing required parameters",
                "details": "layer_id, lng, and lat are required",
            },
            status=400,
        )

    try:
        # Validasi dan parse koordinat
        lng = float(lng)
        lat = float(lat)

        # Validasi range koordinat
        if not (-180 <= lng <= 180) or not (-90 <= lat <= 90):
            return JsonResponse(
                {
                    "error": "Invalid coordinates",
                    "details": "Longitude must be between -180 and 180, Latitude between -90 and 90",
                },
                status=400,
            )

        # Get layer
        layer = get_object_or_404(MasterLayer, pk=layer_id)

        logger.debug(
            f"Querying feature at point ({lng}, {lat}) for layer '{layer.name}' (ID: {layer_id})"
        )

        # Buat point dari koordinat klik
        point = Point(lng, lat, srid=4326)

        # Query fitur yang intersects dengan point
        # ST_Intersects menggunakan GiST index untuk performa tinggi
        feature = FeatureData.objects.filter(
            layer=layer, geometry__intersects=point
        ).first()

        logger.debug(f"Found feature: {feature}")

        if feature:
            # Return data fitur yang ditemukan
            return JsonResponse(
                {
                    "type": "Feature",
                    "id": feature.id,
                    "properties": feature.attributes,
                    "layer_name": layer.name,
                    "layer_id": layer.id,
                }
            )
        else:
            # Tidak ada fitur di lokasi ini
            pass


    except ValueError as e:
        logger.error(f"ValueError in api_feature_at_point: {e}")
        return JsonResponse(
            {
                "error": "Invalid parameter format",
                "details": f"lng and lat must be valid numbers: {str(e)}",
            },
            status=400,
        )
    except Exception as e:
        logger.error(f"Error in api_feature_at_point: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)}, status=500
        )


def expert_drawer_partial(request):
    """Render partial untuk konten drawer tenaga ahli (HTMX) — server-side."""
    feature_result_id = request.GET.get("feature_result_id")
    if feature_result_id:
        return _render_drawer_partial(request, feature_result_id)
    return render(request, "spatial/_expert_drawer.html", {})


# ========== EXPERT REVIEW API ==========

def api_expert_reviews(request):
    """
    API endpoint untuk CRUD review tenaga ahli.

    GET  ?feature_result_id=X  → list semua review untuk fitur tersebut (JSON)
    POST                       → create/update review (form-encoded utk HTMX, JSON utk JS)
    DELETE ?id=X               → hapus review sendiri

    Untuk HTMX: POST/DELETE mengembalikan partial drawer agar konten langsung ter-refresh.
    """
    is_htmx = getattr(request, "htmx", False)

    if request.method == "GET":
        feature_result_id = request.GET.get("feature_result_id")
        if not feature_result_id:
            return JsonResponse({"error": "feature_result_id required"}, status=400)

        reviews = (
            ExpertReview.objects
            .filter(feature_result_id=feature_result_id)
            .select_related("expert")
            .order_by("-created_at")
        )
        data = [
            {
                "id": r.id,
                "expert_name": r.expert.get_full_name() or r.expert.username,
                "notes": r.notes,
                "created_at": r.created_at.strftime("%d %b %Y %H:%M"),
            }
            for r in reviews
        ]
        return JsonResponse({"reviews": data, "count": len(data)})

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=403)

        if is_htmx:
            feature_result_id = request.POST.get("feature_result_id")
            notes = request.POST.get("notes", "").strip()
        else:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            feature_result_id = body.get("feature_result_id")
            notes = body.get("notes", "").strip()

        if not feature_result_id:
            return JsonResponse({"error": "feature_result_id required"}, status=400)
        if not notes:
            return JsonResponse({"error": "notes required"}, status=400)

        feature_result = get_object_or_404(
            SuitabilityAnalysisResultPerFeature, id=feature_result_id
        )

        # Upsert: satu ahli hanya satu review per fitur
        ExpertReview.objects.update_or_create(
            expert=request.user,
            feature_result=feature_result,
            defaults={"notes": notes},
        )

        if is_htmx:
            # Kembalikan drawer partial yang sudah di-refresh
            return _render_drawer_partial(request, feature_result_id)

        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=403)

        review_id = request.GET.get("id") or request.POST.get("id")
        if not review_id:
            return JsonResponse({"error": "id required"}, status=400)

        is_admin = request.user.is_superuser or request.user.has_role("admin")
        if is_admin:
            review = get_object_or_404(ExpertReview, id=review_id)
        else:
            review = get_object_or_404(ExpertReview, id=review_id, expert=request.user)

        feature_result_id = review.feature_result_id
        review.delete()

        if is_htmx:
            return _render_drawer_partial(request, feature_result_id)

        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def _render_drawer_partial(request, feature_result_id):
    """Helper untuk render ulang drawer partial setelah POST/DELETE."""
    from django.shortcuts import render

    context = {"feature_result_id": feature_result_id}
    try:
        result = SuitabilityAnalysisResultPerFeature.objects.select_related(
            "commodity", "feature", "feature__layer"
        ).get(id=feature_result_id)

        context["commodity_name"] = result.commodity.name
        context["suitability_class"] = result.get_suitability_class_display()
        context["suitability_class_code"] = result.suitability_class

        feature_attrs = result.feature.attributes or {}
        context["feature_attrs"] = [
            {"key": k, "value": v}
            for k, v in feature_attrs.items()
            if k not in ("the_geom", "geom", "geometry", "bbox")
        ]

        char_results = result.characteristic_results or []
        context["char_results"] = char_results

        reviews = ExpertReview.objects.filter(
            feature_result=result
        ).select_related("expert").order_by("-created_at")
        context["reviews"] = reviews

        if request.user.is_authenticated:
            my_review = reviews.filter(expert=request.user).first()
            context["my_review"] = my_review

    except SuitabilityAnalysisResultPerFeature.DoesNotExist:
        context["error"] = "Data tidak ditemukan"

    return render(request, "spatial/_expert_drawer.html", context)


def api_feature_at_point_htmx(request):
    """
    API endpoint untuk mendapatkan fitur pada titik tertentu menggunakan ST_Intersects.

    Query parameters:
    - layer_id: ID layer MasterLayer
    - lng: Longitude titik klik
    - lat: Latitude titik klik

    Returns:
    HTML partial untuk HTMX
    """
    from django.contrib.gis.geos import Point

    layer_id = request.GET.get("layer_id")
    lng = request.GET.get("lng")
    lat = request.GET.get("lat")

    # Validasi parameter
    if not all([layer_id, lng, lat]):
        return JsonResponse(
            {
                "error": "Missing required parameters",
                "details": "layer_id, lng, and lat are required",
            },
            status=400,
        )

    try:
        # Validasi dan parse koordinat
        lng = float(lng)
        lat = float(lat)

        # Validasi range koordinat
        if not (-180 <= lng <= 180) or not (-90 <= lat <= 90):
            return JsonResponse(
                {
                    "error": "Invalid coordinates",
                    "details": "Longitude must be between -180 and 180, Latitude between -90 and 90",
                },
                status=400,
            )

        # Get layer
        layer = get_object_or_404(MasterLayer, pk=layer_id)

        logger.debug(
            f"Querying feature at point ({lng}, {lat}) for layer '{layer.name}' (ID: {layer_id})"
        )

        # Buat point dari koordinat klik
        point = Point(lng, lat)
        point.srid = 4326

        # Query fitur yang intersects dengan point
        # ST_Intersects menggunakan GiST index untuk performa tinggi
        feature = FeatureData.objects.filter(
            layer=layer, geometry__intersects=point
        ).first()

        logger.debug(f"Found feature: {feature}")

        if feature:
            # Return data fitur yang ditemukan

            translated_properties = [
                {"key": key, "label": translate_soil_param(key), "value": value}
                for key, value in feature.attributes.items()
            ]

            return render(
                request,
                "partials/feature_detail.html",
                {
                    "type": "Feature",
                    "id": feature.id,
                    "properties": translated_properties,
                    "layer_name": layer.name,
                    "layer_id": layer.id,
                    "lat": lat,
                    "lng": lng,
                    "komoditas": Commodity.objects.all().order_by("group"),
                },
            )
        else:
            pass

    except ValueError as e:
        logger.error(f"ValueError in api_feature_at_point: {e}")
        return JsonResponse(
            {
                "error": "Invalid parameter format",
                "details": f"lng and lat must be valid numbers: {str(e)}",
            },
            status=400,
        )
    except Exception as e:
        logger.error(f"Error in api_feature_at_point: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)}, status=500
        )
