"""
Layer CRUD Views

Handles layer management operations:
- List, detail, toggle, edit, delete layers
- Upload is in upload.py
"""

import logging
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django_htmx.http import trigger_client_event

from apps.master_data.models import DataYear
from apps.spatial.models import MasterLayer
from apps.spatial.forms import LayerEditForm

logger = logging.getLogger(__name__)


# ========== HELPERS ==========

def _get_filtered_layers(request):
    """Helper function untuk filter layer (digunakan di layer_list & layer_list_table)."""
    queryset = MasterLayer.objects.all()

    # Filter berdasarkan active data year (dari session)
    year_id = request.session.get('active_data_year_id')
    if year_id:
        queryset = queryset.filter(data_year_id=year_id)

    search = request.GET.get("search", "")
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(table_name__icontains=search)
        )

    year = request.GET.get("year", "")
    if year:
        try:
            year_int = int(year)
            queryset = queryset.filter(data_year__year=year_int)
        except (ValueError, TypeError):
            pass

    category = request.GET.get("category", "")
    if category:
        queryset = queryset.filter(layer_category=category)

    sort = request.GET.get("sort", "")
    if sort == "name":
        queryset = queryset.order_by("name")
    elif sort == "-name":
        queryset = queryset.order_by("-name")

    queryset = queryset.annotate(feature_count=Count("features"))

    return queryset


# ========== LAYER LIST & MANAGEMENT ==========

@ensure_csrf_cookie
def layer_management(request):
    """
    Unified layer management page: list + map.
    Dual-mode: HTMX request returns panel partial; regular request returns full page.
    """
    queryset = _get_filtered_layers(request)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Build query string for pagination (exclude 'page')
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "layers": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "title": "Layer Management",
        "search": request.GET.get("search", ""),
        "year": request.GET.get("year", ""),
        "category": request.GET.get("category", ""),
        "sort": request.GET.get("sort", ""),
        "data_years": DataYear.objects.all().order_by("-year"),
        "data_categories": MasterLayer.LAYER_CATEGORY_CHOICES,
        "filter_qs": urlencode(params),
    }

    if request.htmx:
        return render(request, "spatial/_layer_list_panel.html", context)

    return render(request, "spatial/layer_management.html", context)



# ========== LAYER DETAIL ==========

def layer_detail(request, pk):
    """
    Menampilkan detail dari satu layer, termasuk daftar fiturnya.
    """
    layer = MasterLayer.objects.get(pk=pk)
    features = layer.features.all()[:10]  # Tampilkan 10 fitur pertama

    context = {
        "layer": layer,
        "features": features,
        "title": f"Detail Layer: {layer.name}",
    }

    return render(request, "spatial/layer_detail.html", context)


# ========== LAYER TOGGLE ==========

@require_http_methods(["POST"])
def layer_toggle(request, pk):
    """
    Toggle layer active status.
    """
    layer = get_object_or_404(MasterLayer, pk=pk)
    layer.is_active = not layer.is_active
    layer.save()

    status = "Aktif" if layer.is_active else "Nonaktif"
    message = f"Layer '{layer.name}' berhasil diubah menjadi {status}"

    toast_html = render_to_string(
        "components/toast.html",
        {"variant": "success", "title": "Berhasil", "message": message},
        request=request,
    )

    return HttpResponse(toast_html)


# ========== LAYER EDIT ==========

@login_required
def layer_edit(request, pk):
    """
    Edit metadata layer (nama, kategori, tahun data).

    Dual-mode: HTMX request returns modal partial; regular request returns full page.
    """
    layer = get_object_or_404(MasterLayer, pk=pk)
    is_htmx = getattr(request, "htmx", False)

    if request.method == "POST":
        form = LayerEditForm(request.POST, instance=layer)
        if form.is_valid():
            form.save()

            if is_htmx:
                toast_html = render_to_string(
                    "components/toast.html",
                    {
                        "variant": "success",
                        "title": "Berhasil",
                        "message": f"Metadata layer \"{layer.name}\" berhasil diperbarui.",
                    },
                    request=request,
                )
                response = HttpResponse(toast_html)
                response["HX-Trigger"] = "modalClose"
                return response

            messages.success(request, f"Metadata layer \"{layer.name}\" berhasil diperbarui.")
            return redirect("spatial:layer_management")
    else:
        form = LayerEditForm(instance=layer)

    if is_htmx:
        return render(request, "spatial/_layer_edit_modal.html", {"form": form, "layer": layer})

    # Non-HTMX: redirect ke management page
    return redirect("spatial:layer_management")


# ========== LAYER DELETE ==========

@require_http_methods(["POST"])
def layer_delete(request, pk):
    """
    Delete layer.
    """
    layer = get_object_or_404(MasterLayer, pk=pk)
    layer_name = layer.name

    try:
        logger.info(f"Deleting layer '{layer_name}' from database...")
        layer.delete()
        logger.info(f"[OK] Layer {layer_name} deleted from database")

        response = HttpResponse()
        trigger_client_event(response, "showMessage", {"icon": "success", "text": f"Layer '{layer_name}' berhasil dihapus"})
        return response

    except Exception as e:
        logger.error(f"Error deleting layer: {e}")

        response = HttpResponse(status=500)
        trigger_client_event(response, "showMessage", {"icon": "error", "text": f"Gagal menghapus layer: {str(e)}"})
        return response
