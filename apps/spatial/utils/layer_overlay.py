"""
Layer Overlay/Spatial Join Utilities

Fungsi untuk menggabungkan multiple layer berdasarkan geometry (spatial join).
Semua layer memiliki poligon yang sama, jadi kita bisa join berdasarkan intersection.

Tahap 2 dari Alur Sistem Rekomendasi:
1. Input Layer (selesai)
2. Penggabungan Layer (overlay/join) ← INI
3. Rule-Based Evaluation
4. Limiting Factor Analysis
"""

import json
import logging
from typing import Dict, List, Any
from django.db import transaction
from django.db.models import Min, Max
from django.contrib.gis.geos import Polygon

from apps.spatial.models import MasterLayer, FeatureData

logger = logging.getLogger(__name__)



def overlay_layers_by_finest_resolution(
    layer_ids: List[int],
    output_layer_name: str,
    output_table_name: str,
    user=None,
    data_year=None,
    bbox=None,
    clip_geometry=None,
    attribute_filter=None,
) -> Dict[str, Any]:
    """
    Menggabungkan layer menggunakan resolusi terhalus.

    Strategy:
    1. Gunakan layer dengan feature count terbanyak sebagai base (resolusi terhalus)
    2. Untuk setiap feature di base layer, cari intersecting features di layer lain
    3. Kumpulkan atribut dari semua layer yang intersect

    Cocok untuk:
    - Layer dengan feature count sangat bervariasi (misal 6 vs 1595)
    - Layer finer-grained (1595 features) meng-cover area yang sama dengan coarser layer (6 features)
    - Semua layer cover area yang sama (kecamatan)

    Args:
        layer_ids: List of layer IDs
        output_layer_name: Nama layer output
        output_table_name: Nama tabel output
        user: User yang melakukan proses
        data_year: Tahun data
        bbox: Optional bounding box filter (min_x, max_x, min_y, max_y)
        clip_geometry: Optional GEOSGeometry untuk clip output
        attribute_filter: Optional dict for filtering by attributes, e.g. {'KECAMATAN': 'Barru'}

    Returns:
        Dict dengan hasil overlay
    """
    import time

    start_time = time.time()

    try:
        # Validasi
        if not layer_ids or len(layer_ids) < 2:
            return {
                "success": False,
                "message": "Minimal 2 layer diperlukan untuk overlay",
            }

        layers = MasterLayer.objects.filter(id__in=layer_ids, is_active=True)
        if layers.count() != len(layer_ids):
            return {
                "success": False,
                "message": "Beberapa layer tidak ditemukan atau tidak aktif",
            }

        logger.info(f"Starting finest resolution overlay for {layers.count()} layers")

        # Cek layer output sudah ada
        if MasterLayer.objects.filter(table_name=output_table_name).exists():
            return {
                "success": False,
                "message": f'Layer dengan nama "{output_table_name}" sudah ada. Gunakan nama lain.',
            }

        # Cari layer dengan feature count terbanyak sebagai base
        layer_feature_counts = []
        for layer in layers:
            count = FeatureData.objects.filter(layer=layer).count()
            layer_feature_counts.append((layer, count))

        # Sort descending by feature count
        layer_feature_counts.sort(key=lambda x: x[1], reverse=True)
        base_layer, base_count = layer_feature_counts[0]

        logger.info(
            f"Using {base_layer.name} (ID: {base_layer.id}, {base_count} features) as base layer"
        )

        with transaction.atomic():
            # Buat output layer
            output_layer = MasterLayer.objects.create(
                name=output_layer_name,
                table_name=output_table_name,
                layer_type="multipolygon",
                layer_category="base_analisis",
                data_year=data_year,
                created_by=user,
                attributes={
                    "overlay_type": "finest_resolution",
                    "base_layer": base_layer.table_name,
                    "base_feature_count": base_count,
                    "source_layers": [l.table_name for l in layers],
                    "layer_count": layers.count(),
                    "layer_feature_counts": {
                        l.table_name: cnt for l, cnt in layer_feature_counts
                    },
                },
                is_active=True,
            )

            # Filter base features by bbox, wilayah, or clip_geometry if provided
            if attribute_filter:
                # Filter by attribute field (e.g., KECAMATAN='Barru')
                # filter_kwargs = {
                #     f"attributes__{key}": value
                #     for key, value in attribute_filter.items()
                # }
                filter_kwargs = {
                    f"{key}": value for key, value in attribute_filter.items()
                }
                base_features = FeatureData.objects.filter(
                    layer=base_layer, **filter_kwargs
                )
                logger.info(f"Attribute filter applied: {attribute_filter}")
            else:
                base_features = FeatureData.objects.filter(layer=base_layer)

            logger.info(f"Processing {base_features.count()} base features")

            features_created = 0
            multiple_intersects = 0  # Track berapa kali ada multiple intersections

            for idx, base_feature in enumerate(base_features, 1):
                if idx % 100 == 0:
                    logger.info(f"Processing feature {idx}/{base_features.count()}")

                base_geom = base_feature.geometry

                # Kumpulkan atribut dari semua layer
                combined_attributes = {}
                # combined_attributes['_base_layer'] = base_layer.name
                # combined_attributes['_base_feature_id'] = base_feature.id

                # Tambahkan atribut dari base layer
                combined_attributes.update(base_feature.attributes)

                # Untuk setiap layer lain (termasuk yang lebih coarse)
                for layer in layers:
                    if layer.id == base_layer.id:
                        continue  # Skip base layer

                    layer_name = layer.name

                    # Cari features yang intersect dengan base geometry
                    intersecting_features = FeatureData.objects.filter(
                        layer=layer, geometry__intersects=base_geom
                    )

                    if intersecting_features.exists():
                        intersect_count = intersecting_features.count()

                        if intersect_count > 1:
                            multiple_intersects += 1
                            logger.warning(
                                f"Base feature {base_feature.id} intersects {intersect_count} "
                                f"features in layer {layer.name}. Taking first."
                            )

                        # Ambil feature pertama yang intersect
                        intersect_feature = intersecting_features.first()

                        # Tambahkan atribut dengan prefix
                        for (
                            attr_name,
                            attr_value,
                        ) in intersect_feature.attributes.items():
                            # prefixed_name = f"{layer_name}_{attr_name}"
                            # combined_attributes[prefixed_name] = attr_value
                            combined_attributes[attr_name] = attr_value

                        # combined_attributes[f"{layer_name}_feature_id"] = intersect_feature.id
                        # combined_attributes[f"{layer_name}_intersect_count"] = intersect_count
                    else:
                        # Tidak ada intersecting feature
                        logger.warning(
                            f"No intersecting feature found for base feature {base_feature.id} "
                            f"in layer {layer.name}"
                        )
                        # combined_attributes[f"{layer_name}_feature_id"] = None
                        # combined_attributes[f"{layer_name}_intersect_count"] = 0

                # Buat feature baru dengan combined attributes
                FeatureData.objects.create(
                    layer=output_layer,
                    geometry=base_geom,
                    attributes=combined_attributes,
                )
                features_created += 1

            logger.info(f"Overlay completed: {features_created} features created")
            if multiple_intersects > 0:
                logger.info(
                    f"Warning: {multiple_intersects} base features had multiple intersections"
                )

            total_time = time.time() - start_time

            return {
                "success": True,
                "output_layer_id": output_layer.id,
                "output_layer_name": output_layer.name,
                "features_created": features_created,
                "base_layer": base_layer.name,
                "base_feature_count": base_count,
                "multiple_intersections": multiple_intersects,
                "source_layer_count": layers.count(),
                "performance": {
                    "total_time_seconds": round(total_time, 2),
                    "time_per_feature": round(total_time / features_created, 3)
                    if features_created > 0
                    else 0,
                    "chunks_processed": "N/A",
                    "chunk_size": "N/A",
                    "parallel_enabled": False,
                    "optimization_method": "n_plus_one_queries",
                },
                "message": f"Berhasil menggabungkan {layers.count()} layer menjadi {features_created} fitur "
                f"menggunakan {base_layer.name} sebagai base (NON-OPTIMIZED: {total_time:.2f}s)",
            }

    except Exception as e:
        logger.error(f"Error in overlay_layers_by_finest_resolution: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}


def overlay_layers_by_finest_resolution_optimized(
    layer_ids: List[int],
    output_layer_name: str,
    output_table_name: str,
    user=None,
    data_year=None,
    bbox=None,
    clip_geometry=None,
    attribute_filter=None,
    chunk_size=500,
    enable_parallel=True,
    verbose_timing=True,
) -> Dict[str, Any]:
    """
    Optimized overlay menggunakan SQL JOIN + PostgreSQL Parallel Query.

    Strategy:
    1. Single batch SQL query dengan JOINs (bukan N+1 queries)
    2. PostgreSQL parallel workers untuk execute query
    3. Chunked processing untuk memory management
    4. Bulk insert untuk batch create features

    Speedup: 10-100x lebih cepat dari versi non-optimized.

    Args:
        layer_ids: List of layer IDs
        output_layer_name: Nama layer output
        output_table_name: Nama tabel output
        user: User yang melakukan proses
        data_year: Tahun data
        bbox: Optional bounding box filter (min_x, max_x, min_y, max_y)
        clip_geometry: Optional GEOSGeometry untuk clip output
        attribute_filter: Optional dict untuk filter atribut, e.g. {'KECAMATAN': 'Barru'}
        chunk_size: Jumlah features per batch (default: 500)
        enable_parallel: Enable PostgreSQL parallel workers (default: True)
        verbose_timing: Log performance metrics (default: True)

    Returns:
        Dict dengan hasil overlay + timing information
    """
    import time
    from django.db import connection

    start_time = time.time()

    try:
        # Validasi
        if not layer_ids or len(layer_ids) < 2:
            return {
                "success": False,
                "message": "Minimal 2 layer diperlukan untuk overlay",
            }

        layers = MasterLayer.objects.filter(id__in=layer_ids, is_active=True)
        if layers.count() != len(layer_ids):
            return {
                "success": False,
                "message": "Beberapa layer tidak ditemukan atau tidak aktif",
            }

        logger.info(
            f"Starting OPTIMIZED finest resolution overlay for {layers.count()} layers"
        )

        # Cek layer output sudah ada
        if MasterLayer.objects.filter(table_name=output_table_name).exists():
            return {
                "success": False,
                "message": f'Layer dengan nama "{output_table_name}" sudah ada. Gunakan nama lain.',
            }

        # Cari layer dengan feature count terbanyak sebagai base
        layer_feature_counts = []
        for layer in layers:
            count = FeatureData.objects.filter(layer=layer).count()
            layer_feature_counts.append((layer, count))

        # Sort descending by feature count
        layer_feature_counts.sort(key=lambda x: x[1], reverse=True)
        base_layer, base_count = layer_feature_counts[0]
        overlay_layer_ids = [layer.id for layer in layers if layer.id != base_layer.id]

        logger.info(
            f"Using {base_layer.name} (ID: {base_layer.id}, {base_count} features) as base layer"
        )
        logger.info(
            f"Overlay layers: {[layer.name for layer in layers if layer.id != base_layer.id]}"
        )

        with transaction.atomic():
            # Buat output layer
            output_layer = MasterLayer.objects.create(
                name=output_layer_name,
                table_name=output_table_name,
                layer_type="multipolygon",
                layer_category="tanah",
                data_year=data_year,
                created_by=user,
                attributes={
                    "overlay_type": "finest_resolution_optimized",
                    "optimization": "sql_join_parallel",
                    "base_layer": base_layer.table_name,
                    "base_feature_count": base_count,
                    "source_layers": [l.table_name for l in layers],
                    "layer_count": layers.count(),
                    "layer_feature_counts": {
                        l.table_name: cnt for l, cnt in layer_feature_counts
                    },
                    "chunk_size": chunk_size,
                    "parallel_enabled": enable_parallel,
                },
                is_active=True,
            )

            # Filter base features by bbox, wilayah, or clip_geometry if provided
            filter_kwargs = {}
            if attribute_filter:
                # Filter by attribute field (e.g., KECAMATAN='Barru')
                for key, value in attribute_filter.items():
                    filter_kwargs[f"attributes__{key}"] = value
                base_features_qs = FeatureData.objects.filter(
                    layer=base_layer, **filter_kwargs
                )
                logger.info(f"Attribute filter applied: {attribute_filter}")
            elif bbox:
                from django.contrib.gis.geos import Polygon as GeosPolygon

                min_x, max_x, min_y, max_y = bbox
                bbox_polygon = GeosPolygon.from_bbox((min_x, min_y, max_x, max_y))
                base_features_qs = FeatureData.objects.filter(
                    layer=base_layer, geometry__intersects=bbox_polygon
                )
                logger.info(f"Bounding box filter applied: {bbox}")
            elif clip_geometry:
                # Filter by polygon geometry (for irregular shapes)
                base_features_qs = FeatureData.objects.filter(
                    layer=base_layer, geometry__intersects=clip_geometry
                )
                logger.info(f"Geometry filter applied")
            else:
                base_features_qs = FeatureData.objects.filter(layer=base_layer)

            total_base_features = base_features_qs.count()
            logger.info(
                f"Processing {total_base_features} base features with {len(overlay_layer_ids)} overlay layers"
            )

            # ========================================
            # KEY OPTIMIZATION: SQL BATCH PROCESSING
            # ========================================

            features_created = 0
            multiple_intersects = 0
            chunk_number = 0

            output_features = []  # Accumulate for bulk insert

            # Process in chunks
            offset = 0
            while offset < total_base_features:
                chunk_number += 1
                chunk_start_time = time.time()

                # Get chunk of base features
                base_features_chunk = list(
                    base_features_qs[offset : offset + chunk_size]
                )
                base_ids_in_chunk = [f.id for f in base_features_chunk]

                logger.info(
                    f"Processing chunk {chunk_number} (features {offset + 1}-{min(offset + chunk_size, total_base_features)})"
                )

                # ✅ KEY OPTIMIZATION: Single SQL query untuk SEMUA intersections di chunk ini
                with connection.cursor() as cursor:
                    # Enable PostgreSQL parallel query
                    if enable_parallel:
                        cursor.execute("SET max_parallel_workers_per_gather = 4;")
                        cursor.execute("SET parallel_tuple_cost = 0.01;")
                        cursor.execute("SET parallel_setup_cost = 100;")

                    # Single batch query dengan JOINs
                    sql = """
                    WITH base_features AS (
                        SELECT
                            id,
                            geometry,
                            attributes
                        FROM spatial_featuredata
                        WHERE layer_id = %s
                        AND id = ANY(%s)
                    ),
                    layer_intersect AS (
                        SELECT
                            bf.id AS base_id,
                            bf.attributes AS base_attrs,
                            ml.id AS layer_id,
                            ml.name AS layer_name,
                            fd.id AS intersect_feature_id,
                            fd.attributes AS intersect_attrs
                        FROM base_features bf
                        CROSS JOIN spatial_masterlayer ml
                        JOIN spatial_featuredata fd ON fd.layer_id = ml.id
                        WHERE ml.id = ANY(%s)
                        AND ST_Intersects(bf.geometry, fd.geometry)
                    )
                    SELECT
                        base_id,
                        layer_id,
                        layer_name,
                        intersect_feature_id,
                        intersect_attrs
                    FROM layer_intersect
                    ORDER BY base_id, layer_id
                    """

                    cursor.execute(
                        sql, [base_layer.id, base_ids_in_chunk, overlay_layer_ids]
                    )

                    # Fetch all results dari single query
                    intersections = cursor.fetchall()

                chunk_query_time = time.time() - chunk_start_time
                logger.info(f"  ├─ Batch query executed in {chunk_query_time:.2f}s")
                logger.info(f"  └─ Found {len(intersections)} intersections")

                # Group intersections by base_id
                grouped = {}
                for row in intersections:
                    base_id = row[0]
                    if base_id not in grouped:
                        grouped[base_id] = []

                    raw_attrs = row[4]  # intersect_attrs dari query

                    # === PARSING AMAN UNTUK JSONB ===
                    if raw_attrs is None:
                        parsed_attrs = {}
                    elif isinstance(raw_attrs, dict):
                        parsed_attrs = raw_attrs  # Sudah dikonversi dengan benar
                    elif isinstance(raw_attrs, str):
                        try:
                            # First decode attempt
                            parsed_attrs = json.loads(raw_attrs)
                            # Handle double-encoded JSON (common issue!)
                            if isinstance(parsed_attrs, str):
                                parsed_attrs = json.loads(parsed_attrs)
                        except (json.JSONDecodeError, TypeError) as e:
                            logger.warning(
                                f"Failed to parse attributes for feature {row[3]}: {e}. "
                                f"Raw value type: {type(raw_attrs)}, preview: {raw_attrs[:150] if isinstance(raw_attrs, str) else raw_attrs}"
                            )
                            parsed_attrs = {}  # Fallback ke empty dict
                    else:
                        logger.warning(
                            f"Unexpected attributes type {type(raw_attrs)} for feature {row[3]}. Using empty dict."
                        )
                        parsed_attrs = {}

                    grouped[base_id].append(
                        {
                            "layer_id": row[1],
                            "layer_name": row[2],
                            "feature_id": row[3],
                            "attributes": parsed_attrs,  # Pasti dictionary
                        }
                    )

                # Create output features
                for base_feature in base_features_chunk:
                    base_id = base_feature.id
                    base_geom = base_feature.geometry

                    # Start with base attributes
                    combined_attributes = {}
                    # combined_attributes['_base_layer'] = base_layer.name
                    # combined_attributes['_base_feature_id'] = base_id
                    combined_attributes.update(base_feature.attributes)

                    # Add intersecting layer attributes
                    if base_id in grouped:
                        for intersect in grouped[base_id]:
                            layer_name = intersect["layer_name"]

                            # Count intersections per layer for this base feature
                            intersect_count = sum(
                                1
                                for i in grouped[base_id]
                                if i["layer_name"] == layer_name
                            )

                            if intersect_count > 1:
                                multiple_intersects += 1
                                logger.debug(
                                    f"Base feature {base_id} intersects {intersect_count} "
                                    f"features in layer {layer_name}. Taking first."
                                )

                            # Add attributes with prefix
                            for attr_name, attr_value in intersect[
                                "attributes"
                            ].items():
                                # prefixed_name = f"{layer_name}_{attr_name}"
                                # combined_attributes[prefixed_name] = attr_value
                                combined_attributes[attr_name] = attr_value

                            # combined_attributes[f"{layer_name}_feature_id"] = intersect['feature_id']
                            # combined_attributes[f"{layer_name}_intersect_count"] = intersect_count
                    else:
                        # No intersections for this base feature
                        for layer in layers:
                            if layer.id == base_layer.id:
                                continue
                            # combined_attributes[f"{layer.name}_feature_id"] = None
                            # combined_attributes[f"{layer.name}_intersect_count"] = 0

                    # Accumulate output feature (untuk bulk insert)
                    output_features.append(
                        FeatureData(
                            layer=output_layer,
                            geometry=base_geom,
                            attributes=combined_attributes,
                        )
                    )
                    features_created += 1

                chunk_total_time = time.time() - chunk_start_time
                logger.info(
                    f"Chunk {chunk_number} completed in {chunk_total_time:.2f}s"
                )

                offset += chunk_size

            # ✅ KEY OPTIMIZATION: Bulk insert (bukan one-by-one)
            logger.info(f"Bulk inserting {len(output_features)} features...")
            bulk_start_time = time.time()

            FeatureData.objects.bulk_create(output_features, batch_size=500)

            bulk_time = time.time() - bulk_start_time
            logger.info(f"Bulk insert completed in {bulk_time:.2f}s")

            total_time = time.time() - start_time

            logger.info(
                f"[OK] OPTIMIZED Overlay completed: {features_created} features created in {total_time:.2f}s"
            )
            if multiple_intersects > 0:
                logger.info(
                    f"[WARNING]  Warning: {multiple_intersects} base features had multiple intersections"
                )

            return {
                "success": True,
                "output_layer_id": output_layer.id,
                "output_layer_name": output_layer.name,
                "features_created": features_created,
                "base_layer": base_layer.name,
                "base_feature_count": base_count,
                "multiple_intersections": multiple_intersects,
                "source_layer_count": layers.count(),
                "performance": {
                    "total_time_seconds": round(total_time, 2),
                    "time_per_feature": round(total_time / features_created, 3)
                    if features_created > 0
                    else 0,
                    "chunks_processed": chunk_number,
                    "chunk_size": chunk_size,
                    "parallel_enabled": enable_parallel,
                    "optimization_method": "sql_join_parallel",
                },
                "message": f"Berhasil menggabungkan {layers.count()} layer menjadi {features_created} fitur "
                f"menggunakan {base_layer.name} sebagai base (OPTIMIZED: {total_time:.2f}s)",
            }

    except Exception as e:
        logger.error(
            f"Error in overlay_layers_by_finest_resolution_optimized: {str(e)}"
        )
        import traceback

        logger.error(traceback.format_exc())
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}


def get_layer_statistics(layer_id: int) -> Dict[str, Any]:
    """
    Mendapatkan statistik layer setelah overlay.
    Berguna untuk quality check.
    """
    try:
        layer = MasterLayer.objects.get(id=layer_id)
        features = FeatureData.objects.filter(layer=layer)

        if not features.exists():
            return {"success": False, "message": "Layer tidak memiliki fitur"}

        # Hitung statistik dasar
        total_features = features.count()

        # Ambil sample untuk analisis atribut
        sample_feature = features.first()

        # Hitung jumlah atribut per fitur
        attr_counts = [f.attributes.keys().__len__() for f in features]

        return {
            "success": True,
            "layer_id": layer_id,
            "layer_name": layer.name,
            "total_features": total_features,
            "min_attributes": min(attr_counts) if attr_counts else 0,
            "max_attributes": max(attr_counts) if attr_counts else 0,
            "avg_attributes": sum(attr_counts) / len(attr_counts) if attr_counts else 0,
            "sample_attributes": list(sample_feature.attributes.keys())
            if sample_feature
            else [],
        }

    except MasterLayer.DoesNotExist:
        return {"success": False, "message": "Layer tidak ditemukan"}
    except Exception as e:
        logger.error(f"Error in get_layer_statistics: {str(e)}")
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}
