"""
Map and GeoJSON Views

Handles map display and GeoJSON API endpoints:
- Map view
- GeoJSON layer API
- Feature at point query
"""
from devtools import debug
import json
import logging

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

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
    Membangun seluruh GeoJSON langsung di PostgreSQL via json_build_object + ST_AsGeoJSON
    untuk performa maksimal (single query, zero Python serialization).
    """
    import time
    from django.db import connection

    t_start = time.perf_counter()

    try:
        layer = MasterLayer.objects.get(pk=pk)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT json_build_object(
                    'type', 'FeatureCollection',
                    'features', COALESCE(json_agg(
                        json_build_object(
                            'type', 'Feature',
                            'properties', attributes,
                            'geometry', ST_AsGeoJSON(geometry)::json
                        )
                    ), '[]'::json)
                )
                FROM spatial_featuredata
                WHERE layer_id = %s
            """, [pk])
            row = cursor.fetchone()

        t_query = time.perf_counter()

        if row and row[0]:
            feature_count = len(row[0].get('features', []))
            t_total = time.perf_counter() - t_start
            t_db = t_query - t_start
            logger.info(
                f"[GeoJSON] layer_id={pk} name='{layer.name}' "
                f"features={feature_count} "
                f"db={t_db*1000:.1f}ms total={t_total*1000:.1f}ms"
            )
            return JsonResponse(row[0], safe=False)

        t_total = time.perf_counter() - t_start
        debug(t_total)
        logger.warning(
            f"[GeoJSON] layer_id={pk} has no features (total={t_total*1000:.1f}ms)"
        )
        return JsonResponse({"type": "FeatureCollection", "features": []})

    except MasterLayer.DoesNotExist:
        logger.error(f"Layer with pk={pk} not found.")
        return JsonResponse({"error": "Layer not found"}, status=404)
    except Exception as e:
        logger.error(
            f"Error generating GeoJSON for layer pk={pk}: {str(e)}", exc_info=True
        )
        return JsonResponse({"error": "An internal server error occurred."}, status=500)


# ========== FEATURE AT POINT API ==========

@csrf_exempt
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
            # return JsonResponse(
            #     {
            #         "info": "Tidak ada data di lokasi ini",
            #         "details": "Coba klik pada area polygon",
            #     }
            # )
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


# ========== EXPERT REVIEW API ==========

@csrf_exempt
def api_expert_reviews(request):
    """
    API endpoint untuk CRUD review tenaga ahli.

    GET  ?feature_result_id=X  → list semua review untuk fitur tersebut
    POST                       → create/update review (expert hanya bisa 1 per fitur)
    DELETE ?id=X               → hapus review sendiri
    """
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
        review, created = ExpertReview.objects.update_or_create(
            expert=request.user,
            feature_result=feature_result,
            defaults={"notes": notes},
        )

        return JsonResponse({
            "id": review.id,
            "expert_name": request.user.get_full_name() or request.user.username,
            "notes": review.notes,
            "created_at": review.created_at.strftime("%d %b %Y %H:%M"),
            "created": created,
        })

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
        review.delete()
        response = JsonResponse({"deleted": True})
        response["HX-Trigger"] = "reviewsUpdated"
        return response

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
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
            # Tidak ada fitur di lokasi ini
            # return JsonResponse(
            #     {
            #         "info": "Tidak ada data di lokasi ini",
            #         "details": "Coba klik pada area polygon",
            #     }
            # )
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



