"""
Layer Upload Views

Handles layer upload operations:
- Upload modal
- Upload processing
- Temp file cleanup
"""

import os
import json
import logging
import shutil
import tempfile

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction

from apps.spatial.models import MasterLayer, FeatureData
from apps.master_data.models import DataYear

logger = logging.getLogger(__name__)


# ========== UPLOAD MODAL ==========

@login_required
def layer_upload_modal(request):
    """Return modal form upload layer."""
    data_years = DataYear.objects.filter(is_active=True).order_by("-year")
    return render(request, "spatial/_layer_upload_modal.html", {"data_years": data_years})


# ========== UPLOAD PROCESSING ==========

@login_required
def layer_upload(request):
    """
    Upload shapefile (zip) dan simpan ke database.
    """
    if request.method != "POST":
        return redirect("spatial:layer_upload_modal")

    try:
        layer_name = request.POST.get("layer_name", "").strip()
        table_name = request.POST.get("table_name", "").strip()
        layer_type = request.POST.get("layer_type", "polygon").strip()
        layer_category = request.POST.get("layer_category", "lainnya").strip()
        data_year_id = request.POST.get("data_year")
        uploaded_file = request.FILES.get("file")

        # Validasi
        if not layer_name:
            return JsonResponse({"success": False, "error": "Nama layer wajib diisi"}, status=400)

        if not table_name:
            table_name = layer_name.lower().replace(" ", "_")

        if not uploaded_file:
            return JsonResponse({"success": False, "error": "File wajib diupload"}, status=400)

        # Validasi duplikasi nama
        if MasterLayer.objects.filter(name=layer_name).exists():
            return JsonResponse({"success": False, "error": f"Layer '{layer_name}' sudah ada"}, status=400)

        # Ambil data year
        data_year = None
        if data_year_id:
            try:
                data_year = DataYear.objects.get(id=data_year_id)
            except DataYear.DoesNotExist:
                pass

        # Proses upload
        result = _handle_layer_upload(
            layer_name=layer_name,
            table_name=table_name,
            layer_type=layer_type,
            layer_category=layer_category,
            data_year=data_year,
            uploaded_file=uploaded_file,
        )

        if result["success"]:
            feature_count = result.get("feature_count", 0)
            messages.success(
                request,
                f"Layer '{layer_name}' berhasil diupload dengan {feature_count} fitur"
            )
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)

    except Exception as e:
        logger.error(f"Error uploading layer: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ========== HELPERS ==========

def _handle_layer_upload(layer_name, table_name, layer_type, layer_category, data_year, uploaded_file):
    """
    Proses upload file shapefile dan simpan ke database.

    Args:
        layer_name: Nama layer yang akan ditampilkan
        table_name: Nama tabel di database
        layer_type: Tipe geometri (polygon, point, dll)
        layer_category: Kategori layer
        data_year: DataYear object atau None
        uploaded_file: File object dari request.FILES

    Returns:
        Dict dengan success, feature_count, dan error jika gagal
    """
    import tempfile
    import zipfile
    import os

    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp dir: {temp_dir}")

    try:
        # Save uploaded zip file
        zip_path = os.path.join(temp_dir, "upload.zip")
        with open(zip_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find .shp file
        shp_file = None
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.endswith(".shp"):
                    shp_file = os.path.join(root, f)
                    break
            if shp_file:
                break

        if not shp_file:
            return {"success": False, "error": "File .shp tidak ditemukan dalam zip"}

        # Read shapefile using GDAL/OGR
        try:
            datasource = DataSource(shp_file)
        except Exception as e:
            logger.error(f"GDAL error reading {shp_file}: {e}")
            return {"success": False, "error": f"Gagal membaca file shapefile: {str(e)}"}

        if datasource.layer_count == 0:
            return {"success": False, "error": "Shapefile tidak memiliki layer"}

        layer = datasource[0]
        srs = layer.srs

        logger.info(
            f"Processing shapefile: {shp_file}, features={len(layer)}, srs={srs}"
        )

        # Create MasterLayer record
        master_layer = MasterLayer.objects.create(
            name=layer_name,
            table_name=table_name,
            layer_type=layer_type,
            layer_category=layer_category,
            data_year=data_year,
        )

        # Import features
        feature_count = 0
        with transaction.atomic():
            for feat in layer:
                geom = feat.geom
                if geom is None:
                    continue

                # Transform to WGS84 if needed
                if geom.srid and geom.srid != 4326:
                    geom.transform(4326)

                geos_geom = GEOSGeometry(geom.wkt, srid=4326)

                # Collect attributes
                attrs = {}
                for field in layer.fields:
                    try:
                        val = feat.get(field)
                        if val is not None:
                            attrs[field] = val
                    except Exception:
                        pass

                FeatureData.objects.create(
                    layer=master_layer,
                    geometry=geos_geom,
                    attributes=attrs,
                )
                feature_count += 1

        logger.info(f"Layer '{layer_name}' created with {feature_count} features")

        return {
            "success": True,
            "feature_count": feature_count,
            "layer_id": master_layer.id,
        }

    except zipfile.BadZipFile:
        return {"success": False, "error": "File yang diupload bukan zip file yang valid"}
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        # Cleanup temp directory
        cleanup_temp_directory(temp_dir)


def cleanup_temp_directory(temp_dir):
    """Bersihkan temporary directory."""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temp dir: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp dir {temp_dir}: {e}")
