"""
Analysis Control Center Views

Pusat kontrol dan monitoring untuk semua proses analisis:
- Dashboard monitoring semua task Celery
- UI untuk batch extraction
- UI untuk batch overlay
- Status real-time progress analisis
"""
from django.http import HttpResponse
import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import escape

from apps.spatial.models import MasterLayer, SuitabilityAnalysisResult
from apps.master_data.models import Commodity, CommodityGroup

logger = logging.getLogger(__name__)


@login_required
def control_center(request):
    """
    Halaman utama Control Center untuk monitoring dan kontrol analisis.
    """
    context = {
        "commodities": Commodity.objects.all(),
        "layers": MasterLayer.objects.all(),
        "commodity_groups": CommodityGroup.objects.all(),
        # "commodities": Commodity.objects.filter(is_active=True),
        # "layers": MasterLayer.objects.filter(is_active=True),
        # "commodity_groups": CommodityGroup.objects.filter(is_active=True),
    }
    return render(request, "analysis/control_center.html", context)


@login_required
def task_monitoring(request):
    """
    Endpoint untuk mendapatkan status monitoring task.
    """
    try:
        # Ambil history analisis terbaru
        recent_analyses = SuitabilityAnalysisResult.objects.select_related(
            'commodity', 'base_layer', 'created_by'
        ).order_by('-created_at')[:20]

        # Hitung statistik
        stats = {
            'total': SuitabilityAnalysisResult.objects.count(),
            'pending': SuitabilityAnalysisResult.objects.filter(status='pending').count(),
            'processing': SuitabilityAnalysisResult.objects.filter(status='processing').count(),
            'completed': SuitabilityAnalysisResult.objects.filter(status='completed').count(),
            'failed': SuitabilityAnalysisResult.objects.filter(status='failed').count(),
        }

        if request.headers.get('HX-Request'):
            # Return HTML partial untuk HTMX
            context = {
                'recent_analyses': recent_analyses,
                'stats': stats,
            }
            return render(request, 'analysis/control/partials/monitoring_panel.html', context)
        else:
            # Return JSON untuk API
            analyses_data = []
            for analysis in recent_analyses:
                analyses_data.append({
                    'id': analysis.id,
                    'commodity': analysis.commodity.name,
                    'layer': analysis.base_layer.name if analysis.base_layer else 'N/A',
                    'status': analysis.status,
                    'progress': analysis.progress_percentage,
                    'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': str(analysis.created_by) if analysis.created_by else 'System',
                })

            return JsonResponse({
                'success': True,
                'stats': stats,
                'analyses': analyses_data,
            })

    except Exception as e:
        logger.error(f"Error in task_monitoring: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def batch_extract_ui(request):
    """
    UI untuk batch extraction layer.
    """
    context = {
        'layers': MasterLayer.objects.filter(is_active=True),
    }
    return render(request, 'analysis/control/partials/batch_extract_form.html', context)


@login_required
def batch_overlay_ui(request):
    """
    UI untuk batch overlay layer.
    """
    context = {
        'layers': MasterLayer.objects.filter(is_active=True),
    }
    return render(request, 'analysis/control/partials/batch_overlay_form.html', context)


@login_required
def suitability_ui(request):
    """
    UI untuk suitability analysis di control center.
    """
    context = {
        'commodities': Commodity.objects.filter(is_active=True),
        'layers': MasterLayer.objects.filter(is_active=True),
    }
    return render(request, 'analysis/control/partials/suitability_form.html', context)


@login_required
def start_analysis_form(request):
    """
    Return form HTML untuk modal start analisis.
    """
    context = {
        'commodities': Commodity.objects.filter(is_active=True),
        'layers': MasterLayer.objects.filter(is_active=True),
    }
    return render(request, 'analysis/control/partials/start_analysis_form.html', context)


@login_required
@require_http_methods(["POST"])
def start_analysis_api(request):
    """
    API endpoint untuk memulai analisis (HTMX response).
    Mendukung multi-komoditas (commodity_ids[]).

    Response:
    - Success: HX-Trigger untuk close modal, toast, dan refresh monitoring
    - Error: Re-render form dengan pesan error
    """
    from apps.analysis.tasks import run_multi_commodity_analysis

    commodity_ids = request.POST.getlist("commodity_ids")
    layer_id = request.POST.get("layer_id")

    if not commodity_ids or not layer_id:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "warning", "message": "Pilih minimal satu komoditas dan layer"}
        })
        return response

    try:
        commodity_ids = [int(c) for c in commodity_ids]
        commodities = Commodity.objects.filter(id__in=commodity_ids)
        layer = MasterLayer.objects.get(id=layer_id)

        if not commodities.exists():
            response = HttpResponse(status=404)
            response["HX-Trigger"] = json.dumps({
                "showToast": {"type": "error", "message": "Komoditas tidak ditemukan"}
            })
            return response

        commodity_names = ", ".join(commodities.values_list("name", flat=True))

        task = run_multi_commodity_analysis.delay(
            commodity_ids=commodity_ids,
            layer_id=layer_id,
            user_id=request.user.id
        )

        response = HttpResponse(status=200)
        response["HX-Trigger"] = json.dumps({
            "showToast": {
                "type": "success",
                "message": f'Analisis {len(commodity_ids)} komoditas ({commodity_names}) pada layer "{layer.name}" telah dimulai'
            },
            "analysisStarted": {}
        })
        return response

    except MasterLayer.DoesNotExist:
        response = HttpResponse(status=404)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "error", "message": "Layer tidak ditemukan"}
        })
        return response
    except (ValueError, TypeError):
        response = HttpResponse(status=400)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "error", "message": "Format data tidak valid"}
        })
        return response
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        response = HttpResponse(status=500)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "error", "message": str(e)}
        })
        return response


@csrf_exempt
@require_http_methods(["POST"])
def delete_analysis(request, result_id):
    """
    Hapus hasil analisis berdasarkan ID.
    Menghapus SuitabilityAnalysisResult beserta SuitabilityAnalysisResultPerFeature terkait.
    """
    try:
        analysis = SuitabilityAnalysisResult.objects.get(id=result_id)
        commodity_name = analysis.commodity.name if analysis.commodity else "N/A"
        analysis.delete()  # CASCADE akan hapus per_feature_results juga

        logger.info(f"[OK] Analysis #{result_id} '{commodity_name}' deleted by {request.user}")

        response = HttpResponse(status=200)
        response["HX-Trigger"] = json.dumps({
            "showToast": {
                "type": "success",
                "message": f'Analisis "{commodity_name}" berhasil dihapus'
            },
            "refreshMonitoring": {}
        })
        return response

    except SuitabilityAnalysisResult.DoesNotExist:
        response = HttpResponse(status=404)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "error", "message": "Analisis tidak ditemukan"}
        })
        return response
    except Exception as e:
        logger.error(f"Error deleting analysis #{result_id}: {e}")
        response = HttpResponse(status=500)
        response["HX-Trigger"] = json.dumps({
            "showToast": {"type": "error", "message": str(e)}
        })
        return response


@csrf_exempt
@require_http_methods(["GET"])
def analysis_status_api(request, result_id=None):
    """
    API endpoint untuk mendapatkan status analisis.
    
    GET /control/status/ - List semua status
    GET /control/status/<id>/ - Status spesifik
    """
    try:
        if result_id:
            analysis = SuitabilityAnalysisResult.objects.get(id=result_id)
            return JsonResponse({
                'success': True,
                'id': analysis.id,
                'status': analysis.status,
                'progress': analysis.progress_percentage,
                'total_features': analysis.total_features,
                's1_count': analysis.s1_count,
                's2_count': analysis.s2_count,
                's3_count': analysis.s3_count,
                'n_count': analysis.n_count,
                'created_at': analysis.created_at.isoformat(),
                'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
            })
        else:
            # List semua status
            analyses = SuitabilityAnalysisResult.objects.select_related(
                'commodity', 'base_layer'
            ).order_by('-created_at')[:50]

            return JsonResponse({
                'success': True,
                'analyses': [{
                    'id': a.id,
                    'commodity': a.commodity.name,
                    'layer': a.base_layer.name if a.base_layer else 'N/A',
                    'status': a.status,
                    'progress': a.progress_percentage,
                    'created_at': a.created_at.isoformat(),
                } for a in analyses]
            })

    except SuitabilityAnalysisResult.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Analysis not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in analysis_status_api: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _htmx_result(message, toast_type, status=200):
    """Respons HTMX: alert inline (sukses/gagal) + toast via HX-Trigger."""
    alert_class = "alert-success" if toast_type == "success" else "alert-error"
    alert_html = (
        f'<div class="alert {alert_class} mt-4"><span>{escape(message)}</span></div>'
    )
    response = HttpResponse(alert_html, status=status)
    response["HX-Trigger"] = json.dumps({
        "showToast": {"type": toast_type, "message": message}
    })
    return response


@login_required
@require_http_methods(["POST"])
def execute_batch_extract(request):
    """
    Jalankan batch extract sebagai task Celery.

    Form mengirim array paralel per baris: source_layer, target_layer, attributes.
    Atribut dipisah koma; satu atribut dikirim sebagai string, lebih dari satu sebagai list.
    """
    from apps.analysis.tasks import run_batch_extract

    sources = request.POST.getlist("source_layer")
    targets = request.POST.getlist("target_layer")
    attributes = request.POST.getlist("attributes")

    if not sources or not (len(sources) == len(targets) == len(attributes)):
        return _htmx_result("Data baris ekstraksi tidak lengkap", "error", status=400)

    extractions = []
    for source, target, attr_text in zip(sources, targets, attributes):
        target = target.strip()
        names = [a.strip() for a in attr_text.split(",") if a.strip()]
        if not source or not target or not names:
            return _htmx_result("Setiap baris wajib diisi layer source, nama target, dan atribut", "error", status=400)
        extractions.append({
            "source_layer": source,
            "target_layer": target,
            "attributes": names[0] if len(names) == 1 else names,
        })

    task = run_batch_extract.delay(extractions=extractions)
    message = f"Batch extract {len(extractions)} konfigurasi dimulai (task {task.id})"
    return _htmx_result(message, "success")


@login_required
@require_http_methods(["POST"])
def execute_batch_overlay(request):
    """
    Jalankan batch overlay sebagai task Celery.

    Parameter (POST form):
    - layer_ids: minimal 2 ID layer
    - output_layer_name: nama layer output
    - method: 'finest_resolution' atau 'finest_resolution_optimized'
    - wilayah: filter KECAMATAN (opsional)
    """
    from apps.analysis.tasks import run_batch_overlay

    layer_ids = [int(x) for x in request.POST.getlist("layer_ids") if x.isdigit()]
    output_name = request.POST.get("output_layer_name", "").strip()
    method = request.POST.get("method", "finest_resolution")
    wilayah = request.POST.get("wilayah", "").strip() or None

    if len(layer_ids) < 2:
        return _htmx_result("Pilih minimal 2 layer untuk overlay", "error", status=400)
    if not output_name:
        return _htmx_result("Nama layer output wajib diisi", "error", status=400)

    task = run_batch_overlay.delay(
        layer_ids=layer_ids,
        output_layer_name=output_name,
        method=method,
        wilayah=wilayah,
        user_id=request.user.id,
    )
    message = f'Batch overlay "{output_name}" dari {len(layer_ids)} layer dimulai (task {task.id})'
    return _htmx_result(message, "success")
