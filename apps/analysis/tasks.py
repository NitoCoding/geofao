"""
Celery Task Sederhana untuk Analisis Kesesuaian Lahan

Task yang hanya menggunakan metode minimum FAO yang sederhana.
"""

from apps.master_data.models import SuitabilityCharacteristic
import logging
from celery import shared_task
from django.utils import timezone
from django.db import connection

from apps.analysis.analysis import analyze_suitability, recommend_crops_for_land
from apps.spatial.models import SuitabilityAnalysisResult, SuitabilityAnalysisResultPerFeature, MasterLayer, FeatureData
from apps.master_data.models import Commodity

logger = logging.getLogger(__name__)


def _build_field_mapping(commodity_id: int = None) -> dict[str, str]:
    """
    Bangun mapping source_field → name dari SuitabilityCharacteristic.

    Args:
        commodity_id: Jika diberikan, hanya ambil karakteristik untuk komoditas itu.
                      Jika None, ambil semua (union) — untuk multi-komoditas.

    Returns:
        Dict {source_field: characteristic_name}
    """
    qs = SuitabilityCharacteristic.objects.exclude(source_field='').filter(is_active=True)
    if commodity_id:
        qs = qs.filter(commodity_id=commodity_id)

    return {c.source_field: c.name for c in qs}


def _extract_soil_data(attrs: dict, commodity_id: int = None) -> dict:
    """Ekstrak dan mapping data tanah dari attributes fitur."""
    soil_data = {}
    field_mapping = _build_field_mapping(commodity_id)

    for source_field, char_name in field_mapping.items():
        if source_field in attrs:
            soil_data[char_name] = attrs[source_field]
    return soil_data


@shared_task
def run_simple_analysis(commodity_id: int, layer_id: int, user_id: int = None) -> dict:
    """
    Task sederhana untuk analisis kesesuaian lahan.
    
    Args:
        commodity_id: ID komoditas
        layer_id: ID layer yang akan dianalisis
        user_id: ID user (optional)
        
    Returns:
        Hasil analisis sederhana
    """
    try:
        logger.info(f"Memulai analisis sederhana untuk komoditas {commodity_id}, layer {layer_id}")
        
        # Ambil data
        layer = MasterLayer.objects.get(id=layer_id)
        commodity = Commodity.objects.get(id=commodity_id)
        
        # Hapus hasil per-poligon lama untuk komoditas+layer ini (hindari konflik unique_together)
        SuitabilityAnalysisResultPerFeature.objects.filter(
            commodity=commodity,
            analysis_layer=layer,
        ).delete()

        # Buat record hasil agregat
        result = SuitabilityAnalysisResult.objects.create(
            commodity=commodity,
            base_layer=layer,
            status='processing',
            analysis_method='minimum',
            created_by_id=user_id,
            started_at=timezone.now()
        )
        
        # Ambil semua fitur dari layer
        features = FeatureData.objects.filter(layer=layer)
        total_features = features.count()
        
        if total_features == 0:
            result.status = 'completed'
            result.completed_at = timezone.now()
            result.save()
            return {
                'success': True,
                'result_id': result.id,
                'message': 'Tidak ada fitur untuk dianalisis'
            }
        
        # Inisialisasi counter
        s1_count = 0
        s2_count = 0
        s3_count = 0
        n_count = 0
        unknown_count = 0
        
        # Batch untuk menyimpan per-poligon ke DB
        per_feature_results = []
        BATCH_SIZE = 100

        # Proses setiap fitur
        for idx, feature in enumerate(features):
            # Ekstrak data tanah dari attributes
            soil_data = _extract_soil_data(feature.attributes, commodity_id)

            # DEBUG: log pertama dan kedua poligon untuk verifikasi
            if idx == 0:
                field_mapping = _build_field_mapping(commodity_id)
                logger.error(f"DEBUG: feature.attributes keys = {list(feature.attributes.keys())[:10]}")
                logger.error(f"DEBUG: field_mapping = {field_mapping}")
                logger.error(f"DEBUG: soil_data = {soil_data}")
                logger.error(f"DEBUG: soil_data kosong = {not soil_data}")
            
            # logger.info(f"Ekstrak data tanah untuk fitur {idx+1}/{total_features}: {soil_data}")
            
            # Jika ada data tanah, lakukan analisis
            if soil_data:
                analysis_result = analyze_suitability(commodity_id, soil_data)
                
                # Update counter berdasarkan kelas
                overall_class = analysis_result.get('overall_class', 'Unknown')
                if overall_class == 'S1':
                    s1_count += 1
                elif overall_class == 'S2':
                    s2_count += 1
                elif overall_class == 'S3':
                    s3_count += 1
                elif overall_class == 'N':
                    n_count += 1
                else:
                    unknown_count += 1

                # Simpan hasil per-poligon ke list untuk batch insert
                per_feature_results.append(
                    SuitabilityAnalysisResultPerFeature(
                        commodity=commodity,
                        feature=feature,
                        analysis_layer=layer,
                        parent_result=result,
                        suitability_class=overall_class,
                        suitability_score=analysis_result.get('overall_score', 0),
                        characteristic_results=analysis_result.get('characteristics', []),
                    )
                )

            # Batch insert setiap BATCH_SIZE fitur
            if len(per_feature_results) >= BATCH_SIZE:
                SuitabilityAnalysisResultPerFeature.objects.bulk_create(
                    per_feature_results,
                    ignore_conflicts=True  # hindari duplikasi jika re-run
                )
                logger.info(f"Batch insert: {len(per_feature_results)} per-feature results")
                per_feature_results.clear()

            # Update progress setiap 10 fitur
            if (idx + 1) % 10 == 0:
                progress = int(((idx + 1) / total_features) * 100)
                result.progress_percentage = progress
                result.save(update_fields=['progress_percentage'])

        # Simpan sisa hasil yang belum di-insert
        if per_feature_results:
            SuitabilityAnalysisResultPerFeature.objects.bulk_create(
                per_feature_results,
                ignore_conflicts=True
            )
            logger.info(
                f"Final batch insert: {len(per_feature_results)} per-feature results"
            )
        
        # Update hasil akhir
        result.status = 'completed'
        result.completed_at = timezone.now()
        result.total_features = total_features
        result.s1_count = s1_count
        result.s2_count = s2_count
        result.s3_count = s3_count
        result.n_count = n_count
        result.unknown_count = unknown_count
        result.progress_percentage = 100
        result.save()
        
        logger.info(
            f"Analisis selesai: {s1_count} S1, {s2_count} S2, "
            f"{s3_count} S3, {n_count} N, {unknown_count} Unknown | "
            f"Disimpan: {total_features} hasil per-poligon"
        )
        
        return {
            'success': True,
            'result_id': result.id,
            'total_features': total_features,
            's1_count': s1_count,
            's2_count': s2_count,
            's3_count': s3_count,
            'n_count': n_count,
            'unknown_count': unknown_count,
            'message': 'Analisis sederhana selesai'
        }
        
    except Exception as e:
        logger.error(f"Error dalam task sederhana: {e}")
        
        # Update status jika result sudah dibuat
        try:
            result.status = 'failed'
            result.error_message = str(e)
            result.completed_at = timezone.now()
            result.save()
        except:
            pass
            
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def run_multi_commodity_analysis(
    commodity_ids: list[int],
    layer_id: int,
    user_id: int = None
) -> dict:
    """
    Task analisis multi-komoditas: menjalankan analisis untuk semua komoditas
    yang dipilih pada setiap poligon di layer yang sama.

    Args:
        commodity_ids: List ID komoditas yang akan dianalisis
        layer_id: ID layer yang akan dianalisis
        user_id: ID user (optional)

    Returns:
        Hasil analisis multi-komoditas
    """
    try:
        logger.info(
            f"Memulai analisis multi-komoditas: {len(commodity_ids)} komoditas, "
            f"layer {layer_id}"
        )

        layer = MasterLayer.objects.get(id=layer_id)
        features = FeatureData.objects.filter(layer=layer)
        total_features = features.count()

        if total_features == 0:
            return {
                'success': True,
                'message': 'Tidak ada fitur untuk dianalisis',
                'results': []
            }

        result_ids = []

        for commodity_id in commodity_ids:
            # Reuse run_simple_analysis untuk setiap komoditas
            task_result = run_simple_analysis(
                commodity_id=commodity_id,
                layer_id=layer_id,
                user_id=user_id
            )
            result_ids.append(task_result.get('result_id'))

        logger.info(f"Analisis multi-komoditas selesai: {len(result_ids)} record hasil")

        return {
            'success': True,
            'result_ids': result_ids,
            'total_commodities': len(commodity_ids),
            'total_features': total_features,
            'message': 'Analisis multi-komoditas selesai'
        }

    except Exception as e:
        logger.error(f"Error dalam task multi-komoditas: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def run_batch_extract(extractions: list[dict]) -> dict:
    """
    Ekstrak atribut dari beberapa layer source ke layer target (background).

    Args:
        extractions: List dict {source_layer, target_layer, attributes}
    """
    from apps.spatial.utils.layer_extraction import batch_extract_attributes

    logger.info(f"Memulai batch extract: {len(extractions)} konfigurasi")
    result = batch_extract_attributes(extractions)
    logger.info(
        f"Batch extract selesai: {len(result['successful'])} berhasil, "
        f"{len(result['failed'])} gagal"
    )
    return result


@shared_task
def run_batch_overlay(
    layer_ids: list[int],
    output_layer_name: str,
    method: str = 'finest_resolution',
    wilayah: str = None,
    user_id: int = None,
) -> dict:
    """
    Overlay beberapa layer menjadi satu layer gabungan (background).

    Args:
        layer_ids: List ID layer yang akan di-overlay
        output_layer_name: Nama layer output
        method: 'finest_resolution' atau 'finest_resolution_optimized'
        wilayah: Filter opsional berdasarkan KECAMATAN
        user_id: ID user pembuat
    """
    from django.contrib.auth import get_user_model
    from apps.spatial.utils.layer_overlay import (
        overlay_layers_by_finest_resolution,
        overlay_layers_by_finest_resolution_optimized,
    )

    logger.info(
        f"Memulai batch overlay '{output_layer_name}': {len(layer_ids)} layer, metode {method}"
    )
    user = get_user_model().objects.filter(id=user_id).first() if user_id else None
    output_table = f"layer_{output_layer_name.lower().replace(' ', '_')}"
    attribute_filter = {"KECAMATAN": wilayah} if wilayah else None

    overlay_func = (
        overlay_layers_by_finest_resolution_optimized
        if method == 'finest_resolution_optimized'
        else overlay_layers_by_finest_resolution
    )
    return overlay_func(
        layer_ids=layer_ids,
        output_layer_name=output_layer_name,
        output_table_name=output_table,
        user=user,
        attribute_filter=attribute_filter,
    )


@shared_task
def run_crop_recommendation_analysis(
    layer_id: int,
    user_id: int = None
) -> dict:
    """
    Task rekomendasi tanaman: untuk setiap poligon di layer, analisis semua
    komoditas dan simpan yang S1/S2 sebagai "rekomendasi".

    Args:
        layer_id: ID layer yang akan dianalisis
        user_id: ID user (optional)

    Returns:
        Hasil rekomendasi per poligon
    """
    try:
        logger.info(
            f"Memulai analisis rekomendasi untuk layer {layer_id}"
        )

        layer = MasterLayer.objects.get(id=layer_id)
        features = FeatureData.objects.filter(layer=layer)
        total_features = features.count()

        if total_features == 0:
            return {
                'success': True,
                'message': 'Tidak ada fitur untuk dianalisis',
                'recommendation_count': 0
            }

        # Buat record hasil analisis
        result = SuitabilityAnalysisResult.objects.create(
            commodity=None,  # multi-komoditas
            base_layer=layer,
            status='processing',
            analysis_method='minimum',
            created_by_id=user_id,
            started_at=timezone.now()
        )

        recommendation_count = 0
        processed = 0

        for idx, feature in enumerate(features):
            # Ekstrak data tanah dari attributes
            soil_data = _extract_soil_data(feature.attributes)

            if soil_data:
                # Rekomendasikan semua komoditas yang cocok untuk poligon ini
                recs = recommend_crops_for_land(
                    soil_data,
                    include_limiting_factors=False
                )
                recommendation_count += len(recs)
                processed += 1

            # Update progress setiap 10 fitur
            if (idx + 1) % 10 == 0:
                progress = int(((idx + 1) / total_features) * 100)
                result.progress_percentage = progress
                result.save(update_fields=['progress_percentage'])

        # Update hasil akhir
        result.status = 'completed'
        result.completed_at = timezone.now()
        result.total_features = processed
        result.progress_percentage = 100
        result.save()

        logger.info(
            f"Rekomendasi selesai: {recommendation_count} rekomendasi "
            f"dari {total_features} poligon"
        )

        return {
            'success': True,
            'result_id': result.id,
            'total_features': total_features,
            'processed_features': processed,
            'recommendation_count': recommendation_count,
            'message': 'Analisis rekomendasi selesai'
        }

    except Exception as e:
        logger.error(f"Error dalam task rekomendasi: {e}")

        try:
            result.status = 'failed'
            result.error_message = str(e)
            result.completed_at = timezone.now()
            result.save()
        except:
            pass

        return {
            'success': False,
            'error': str(e)
        }
