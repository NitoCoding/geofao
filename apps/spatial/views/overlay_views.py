"""
Layer Overlay Views

Handles API endpoints for layer overlay operations:
- Overlay multiple layers
- Layer statistics
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


# ========== LAYER OVERLAY API ENDPOINTS ==========

@csrf_exempt
@require_http_methods(["POST"])
def api_overlay_layers(request):
    """
    API endpoint untuk overlay/penggabungan multiple layer.

    Parameters:
    - layer_ids: List of layer IDs to overlay
    - output_layer_name: Nama layer output
    - output_table_name: Nama tabel output (optional)
    - method: 'finest_resolution', or 'finest_resolution_optimized' (default: 'finest_resolution')
    - bbox: Optional bounding box filter [min_x, min_y, max_x, max_y]
    - wilayah: Optional filter by KECAMATAN field (e.g., "Barru")
    - attribute_filter: Optional dict for attribute filtering (e.g., {"KECAMATAN": "Barru"})
    - chunk_size: Chunk size for optimized method (default: 500)

    Returns:
    JSON dengan hasil overlay
    """
    from apps.spatial.utils.layer_overlay import (
        overlay_layers_by_finest_resolution,
        overlay_layers_by_finest_resolution_optimized
    )

    try:
        data = json.loads(request.body)

        layer_ids = data.get("layer_ids", [])
        output_name = data.get("output_layer_name")
        output_table = data.get("output_table_name")
        method = data.get("method", "finest_resolution")
        grid_size = data.get("grid_size", 0.01)
        bbox = data.get("bbox")  # [min_x, min_y, max_x, max_y]
        wilayah = data.get("wilayah")  # String kecamatan
        attribute_filter = data.get("attribute_filter")  # Dict
        chunk_size = data.get("chunk_size", 500)  # For optimized method

        # Validasi
        if not layer_ids:
            return JsonResponse({
                "success": False,
                "error": "layer_ids is required"
            }, status=400)

        if not output_name:
            return JsonResponse({
                "success": False,
                "error": "output_layer_name is required"
            }, status=400)

        # Generate table name jika tidak ditentukan
        if not output_table:
            output_table = f"layer_{output_name.lower().replace(' ', '_')}"

        # Build attribute filter if wilayah is provided
        if wilayah and not attribute_filter:
            attribute_filter = {"KECAMATAN": wilayah}

        # Jalankan overlay
        if method == "finest_resolution":
            result = overlay_layers_by_finest_resolution(
                layer_ids=layer_ids,
                output_layer_name=output_name,
                output_table_name=output_table,
                user=request.user if request.user.is_authenticated else None,
                bbox=bbox,
                attribute_filter=attribute_filter
            )
        elif method == "finest_resolution_optimized":
            result = overlay_layers_by_finest_resolution_optimized(
                layer_ids=layer_ids,
                output_layer_name=output_name,
                output_table_name=output_table,
                user=request.user if request.user.is_authenticated else None,
                bbox=bbox,
                attribute_filter=attribute_filter,
                chunk_size=chunk_size,
                enable_parallel=True,
                verbose_timing=True
            )
        else:
            return JsonResponse({
                "success": False,
                "error": f"Unknown method: {method}. Valid methods: intersection, centroid, grid_sampling, finest_resolution, finest_resolution_optimized"
            }, status=400)

        if result.get("success"):
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON payload"
        }, status=400)
    except Exception as e:
        logger.error(f"Error in api_overlay_layers: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_layer_statistics(request, layer_id):
    """
    API endpoint untuk mendapatkan statistik layer.

    Parameters:
    - layer_id: ID layer

    Returns:
    JSON dengan statistik layer
    """
    from apps.spatial.utils.layer_overlay import get_layer_statistics

    try:
        stat = get_layer_statistics(layer_id)

        if stat.get("success"):
            return JsonResponse(stat)
        else:
            return JsonResponse(stat, status=400)

    except Exception as e:
        logger.error(f"Error in api_layer_statistics: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
