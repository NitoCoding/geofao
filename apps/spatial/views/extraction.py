"""
Layer Extraction Views

Handles API endpoints for layer attribute extraction:
- Single attribute extraction
- Multiple attributes extraction
- Batch extraction
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


# ========== LAYER EXTRACTION API ENDPOINTS ==========

@require_http_methods(["GET", "POST"])
def api_extract_layer_attribute(request):
    """
    API endpoint untuk ekstraksi atribut layer.

    GET: List atribut dari layer
    POST: Ekstrak atribut dan buat layer baru

    CSRF dilindungi via header X-CSRFToken (dikirim oleh JavaScript frontend).

    Parameters (GET):
    - source_layer: Nama layer source

    Parameters (POST):
    - source_layer: Nama layer source
    - target_layer: Nama layer target baru
    - attribute: Nama atribut yang diekstrak (single) atau 'multiple'
    - target_attr: Nama atribut di target (optional)
    - attributes: List atribut (jika mode multiple)
    - layer_category: Kategori layer (default: 'tanah')

    Returns:
    JSON dengan hasil ekstraksi
    """
    from apps.spatial.utils.layer_extraction import (
        extract_layer_attribute,
        extract_multiple_attributes,
        list_layer_attributes
    )

    if request.method == "GET":
        source_layer = request.GET.get("source_layer")

        if not source_layer:
            return JsonResponse({
                "success": False,
                "error": "Missing parameter: source_layer"
            }, status=400)

        result = list_layer_attributes(source_layer)

        if result.get("success"):
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)

    else:  # POST
        try:
            data = json.loads(request.body)

            source_layer = data.get("source_layer")
            target_layer = data.get("target_layer")
            attribute = data.get("attribute")
            layer_category = data.get("layer_category", "tanah")

            if not all([source_layer, target_layer, attribute]):
                return JsonResponse({
                    "success": False,
                    "error": "Missing required parameters: source_layer, target_layer, attribute"
                }, status=400)

            if attribute != "multiple":
                result = extract_layer_attribute(
                    source_layer_name=source_layer,
                    target_layer_name=target_layer,
                    attribute_name=attribute,
                    target_attribute_name=data.get("target_attr"),
                    layer_category=layer_category,
                    user=request.user if request.user.is_authenticated else None
                )
            else:
                attributes = data.get("attributes", [])
                if not attributes:
                    return JsonResponse({
                        "success": False,
                        "error": "attributes parameter required for multiple mode"
                    }, status=400)

                result = extract_multiple_attributes(
                    source_layer_name=source_layer,
                    target_layer_name=target_layer,
                    attribute_names=attributes,
                    layer_category=layer_category,
                    user=request.user if request.user.is_authenticated else None
                )

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
            logger.error(f"Error in api_extract_layer_attribute: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)


@require_http_methods(["POST"])
def api_batch_extract_layers(request):
    """
    API endpoint untuk batch ekstraksi layer.

    CSRF dilindungi via header X-CSRFToken (dikirim oleh JavaScript frontend).

    Parameters:
    - extractions: List of dict with format:
        {
            'source_layer': str,
            'target_layer': str,
            'attributes': list or str,
            'target_attribute_name': str (optional)
        }

    Returns:
    JSON dengan hasil batch extraction
    """
    from apps.spatial.utils.layer_extraction import batch_extract_attributes

    try:
        data = json.loads(request.body)
        extractions = data.get("extractions", [])

        if not extractions:
            return JsonResponse({
                "success": False,
                "error": "extractions parameter required"
            }, status=400)

        result = batch_extract_attributes(extractions)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON payload"
        }, status=400)
    except Exception as e:
        logger.error(f"Error in api_batch_extract_layers: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
