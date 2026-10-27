"""
Layer CRUD Views

Handles layer management operations:
- List, upload, detail, toggle, delete layers
"""

import uuid
import os
import shutil
import logging
import json
import zipfile
import devtools

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
from django.contrib.gis.gdal import DataSource
from django_htmx.http import trigger_client_event
from apps.master_data.models import DataYear
from apps.spatial.models import MasterLayer, FeatureData
from apps.spatial.forms import LayerUploadForm, LayerEditForm

logger = logging.getLogger(__name__)



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




@ensure_csrf_cookie
def layer_management(request):
    """
    Unified layer management page: list + map.
    """
    queryset = _get_filtered_layers(request)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "layers": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "title": "Layer Management",
        "search": request.GET.get("search", ""),
        "year": request.GET.get("year", ""),
        "category": request.GET.get("category", ""),
        "sort": request.GET.get("sort", ""),
        "data_years": DataYear.objects.filter(is_active=True).order_by("-year"),
        "data_categories": MasterLayer.LAYER_CATEGORY_CHOICES,
    }

    return render(request, "spatial/layer_management.html", context)


@ensure_csrf_cookie
def layer_list(request):
    """Tampilan daftar layer."""
    queryset = _get_filtered_layers(request)

    # Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "layers": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "title": "Daftar Layer",
        "search": request.GET.get("search", ""),
        "year": request.GET.get("year", ""),
        "category": request.GET.get("category", ""),
        "sort": request.GET.get("sort", ""),
        "data_years": DataYear.objects.filter(is_active=True).order_by("-year"),
        "data_categories": MasterLayer.LAYER_CATEGORY_CHOICES,
    }

    return render(request, "spatial/layer_list.html", context)


def layer_list_table(request):
    """Partial view untuk tabel daftar layer (HTMX)."""
    queryset = _get_filtered_layers(request)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "layers": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "search": request.GET.get("search", ""),
        "year": request.GET.get("year", ""),
        "category": request.GET.get("category", ""),
        "sort": request.GET.get("sort", ""),
    }

    # Return panel partial if requested (for management page)
    if request.GET.get("view") == "panel":
        return render(request, "spatial/_layer_list_panel.html", context)

    return render(request, "spatial/layer_list_table.html", context)




@login_required(login_url="/iam/login/")
def layer_upload_modal(request):
    """
    Return upload form partial for modal (HTMX).
    """
    form = LayerUploadForm()
    return render(request, "spatial/_layer_upload_modal.html", {"form": form})


@login_required(login_url="/iam/login/")
def layer_upload(request):
    """
    Upload dan proses layer spasial dari shapefile.
    """
    if request.method == "POST":
        form = LayerUploadForm(request.POST, request.FILES)

        if form.is_valid():
            return _handle_layer_upload(request, form)
        else:
            # Form tidak valid
            logger.error(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                logger.error(f"  {field}: {errors}")
            messages.error(request, "Form tidak valid. Silakan periksa input Anda.")
    else:
        # GET request - tampilkan form kosong
        form = LayerUploadForm()

    return render(request, "spatial/layer_upload.html", {"form": form})


def _handle_layer_upload(request, form):
    """
    Helper function untuk handle upload layer (dipisah untuk readability).
    """
    logger.info("layer_upload called - Method: POST")
    logger.info(f"POST data: {request.POST}")
    logger.info(f"FILES: {request.FILES}")

    layer_instance = None
    temp_dir_path = None
    ds = None

    try:
        # 1. Simpan MasterLayer (tanpa commit dulu)
        layer_instance = form.save(commit=False)
        layer_instance.created_by = request.user
        layer_instance.table_name = (
            f"layer_{layer_instance.name.lower().replace(' ', '_')}"
        )
        layer_instance.save()

        # 2. Buat direktori sementara unik
        temp_dir_name = f"temp_{uuid.uuid4().hex}"
        temp_dir_path = os.path.join(settings.MEDIA_ROOT, "temp", temp_dir_name)
        os.makedirs(temp_dir_path, exist_ok=True)

        # 3. Ekstrak ZIP
        shapefile = request.FILES["shapefile"]
        with zipfile.ZipFile(shapefile, "r") as zip_ref:
            zip_ref.extractall(temp_dir_path)

        # 4. Cari file .shp
        shp_path = None
        for file in os.listdir(temp_dir_path):
            if file.endswith(".shp"):
                shp_path = os.path.join(temp_dir_path, file)
                break

        if not shp_path:
            raise ValueError("File .shp tidak ditemukan di dalam arsip ZIP.")

        # shp_path = os.path.normpath(shp_path)

        # 5. Baca dengan GDAL
        ds = DataSource(shp_path)
        devtools.debug(ds)
        ogr_layer = ds[0]
        devtools.debug(ogr_layer)

        # 5b. Auto-detect tipe geometri dari shapefile
        gdal_type = str(ogr_layer.geom_type)
        devtools.debug(gdal_type)
        devtools.debug(ogr_layer.geom_type.name)
        TYPE_MAP = {
            'Point': 'point',
            'MultiPoint': 'point',
            'LineString': 'linestring',
            'MultiLineString': 'linestring',
            'Polygon': 'polygon',
            'MultiPolygon': 'multipolygon',
        }
        detected = TYPE_MAP.get(gdal_type)
        if not detected:
            raise ValueError(
                f"Tipe geometri '{gdal_type}' tidak didukung. "
                f"Hanya Point, LineString, Polygon, MultiPolygon dan varian Multi-nya."
            )
        if len(ogr_layer) == 0:
            raise ValueError("Shapefile di dalam ZIP tidak memiliki fitur (0 record).")

        layer_instance.layer_type = detected
        layer_instance.save(update_fields=['layer_type'])

        # 6. Simpan fitur ke database (geometri invalid diperbaiki, geometri kosong dilewati)
        fixed_count = 0
        skipped_count = 0
        for feature in ogr_layer:
            geos = feature.geom.transform(4326, clone=True).geos
            if geos is None or geos.empty:
                skipped_count += 1
                continue
            if not geos.valid:
                geos = geos.make_valid()
                fixed_count += 1

            attrs = {
                field_name: feature.get(field_name) for field_name in ogr_layer.fields
            }

            FeatureData.objects.create(
                layer=layer_instance, geometry=geos, attributes=attrs
            )

        if FeatureData.objects.filter(layer=layer_instance).count() == 0:
            raise ValueError("Tidak ada fitur dengan geometri valid di dalam shapefile.")

        summary = ""
        if fixed_count:
            summary += f" {fixed_count} geometri invalid diperbaiki otomatis."
        if skipped_count:
            summary += f" {skipped_count} fitur tanpa geometri dilewati."
        messages.success(
            request,
            f"Layer '{layer_instance.name}' berhasil diupload dan diproses!{summary}",
        )

        # HTMX request → return list partial + close modal trigger
        if request.htmx:
            request.GET = request.GET.copy()
            request.GET["view"] = "panel"
            response = layer_list_table(request)
            trigger_client_event(response, "closeModal", {})
            return response

        return redirect("spatial:layer_detail", pk=layer_instance.pk)

    except Exception as e:
        error_msg = f"Terjadi kesalahan: {str(e)}"
        logger.error(error_msg)
        messages.error(request, error_msg)

        # Hapus instance jika sudah tersimpan
        if layer_instance and layer_instance.pk:
            layer_instance.delete()

        if request.htmx:
            form = LayerUploadForm(request.POST, request.FILES) if request.method == "POST" else LayerUploadForm()
            return render(request, "spatial/_layer_upload_modal.html", {"form": form})

        return render(request, "spatial/layer_upload.html", {"form": form})

    finally:
        # Lepaskan handle GDAL sebelum membersihkan direktori temp
        ogr_layer = None
        ds = None
        # 8. Bersihkan direktori temp
        if temp_dir_path and os.path.exists(temp_dir_path):
            cleanup_temp_directory(temp_dir_path)


def cleanup_temp_directory(temp_dir_path, max_retries=5, retry_delay=1.0):
    """
    Fungsi helper untuk membersihkan direktori temporer dengan retry mechanism.

    Args:
        temp_dir_path: Path ke direktori temporer yang akan dihapus
        max_retries: Jumlah maksimal percobaan (default: 5)
        retry_delay: Delay antara retry dalam detik (default: 1.0)
    """
    import time
    import gc

    logger.info(f"Attempting to clean up temp directory: {temp_dir_path}")

    # Force garbage collection untuk memastikan GDAL melepaskan file handles
    gc.collect()

    for attempt in range(max_retries):
        try:
            # Coba hapus folder dan seluruh isinya
            if os.path.exists(temp_dir_path):
                shutil.rmtree(temp_dir_path)
                logger.info(
                    f"[OK] Successfully cleaned up temp directory (attempt {attempt + 1})"
                )
                return True

        except PermissionError as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries}: File still locked, waiting {retry_delay}s..."
                )
                time.sleep(retry_delay)
                # Force GC lagi setelah wait
                gc.collect()
            else:
                logger.warning(
                    f"[FAIL] Failed to clean up after {max_retries} attempts: {temp_dir_path}"
                )
                logger.warning(
                    "File akan otomatis terhapus pada server restart berikutnya"
                )

                # Jadwalkan cleanup untuk background thread sebagai last resort
                try:
                    import threading

                    def delayed_cleanup():
                        time.sleep(3)
                        try:
                            if os.path.exists(temp_dir_path):
                                shutil.rmtree(temp_dir_path)
                                logger.info(
                                    f"[OK] Background cleanup successful for: {temp_dir_path}"
                                )
                        except Exception:
                            pass

                    cleanup_thread = threading.Thread(
                        target=delayed_cleanup, daemon=True
                    )
                    cleanup_thread.start()
                except Exception:
                    logger.error(f"[FAIL] Unexpected error during cleanup: {e}")
                    pass

        except Exception as e:
            logger.error(f"[FAIL] Unexpected error during cleanup: {e}")
            break

    return False



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

    # Return toast HTML untuk htmx
    toast_html = render_to_string(
        "components/toast.html",
        {"variant": "success", "title": "Berhasil", "message": message},
        request=request,
    )

    return HttpResponse(toast_html)


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
                # Close modal + refresh layer list via toast + list reload
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
                response["HX-Trigger-After-Settle"] = "closeModal"
                return response

            messages.success(request, f"Metadata layer \"{layer.name}\" berhasil diperbarui.")
            return redirect("spatial:layer_management")
    else:
        form = LayerEditForm(instance=layer)

    if is_htmx:
        return render(request, "spatial/_layer_edit_modal.html", {"form": form, "layer": layer})

    return render(
        request,
        "spatial/layer_edit.html",
        {
            "page_title": "Edit Metadata Layer",
            "form": form,
            "layer": layer,
        },
    )


@require_http_methods(["POST"])
def layer_delete(request, pk):
    """
    Delete layer.
    """
    layer = get_object_or_404(MasterLayer, pk=pk)
    layer_name = layer.name
    table_name = layer.table_name

    try:
        # Hapus layer dari database
        logger.info(f"Deleting layer '{layer_name}' from database...")
        layer.delete()
        logger.info(f"[OK] Layer {layer_name} deleted from database")

        # Return toast success
 

        response = HttpResponse()
        trigger_client_event(response, "showMessage", {"icon": "success", "text": f"Layer '{layer_name}' berhasil dihapus"})
        return response

    except Exception as e:
        logger.error(f"Error deleting layer: {e}")



        response = HttpResponse( status=500)
        trigger_client_event(response, "showMessage", {"icon": "error", "text": f"Gagal menghapus layer: {str(e)}"})
        return response



