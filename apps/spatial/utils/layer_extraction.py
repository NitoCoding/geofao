"""
Layer Extraction Utilities

Fungsi untuk mengekstrak atribut dari layer yang sudah ada
dan membuat layer/tabel baru dengan atribut tersebut.
"""

from django.db import transaction
from apps.spatial.models import MasterLayer, FeatureData
from django.contrib.gis.geos import GEOSGeometry
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _create_extracted_layer(
    source_layer_name,
    target_layer_name,
    layer_category,
    data_year,
    user,
    extraction_metadata,
    attribute_processor
):
    """
    Common layer creation logic for single/multiple attribute extraction.

    Private helper function that handles the shared logic between
    extract_layer_attribute and extract_multiple_attributes.

    Args:
        source_layer_name (str): Nama layer source
        target_layer_name (str): Nama layer target baru
        layer_category (str): Kategori layer ('tanah', 'komoditas', 'lainnya')
        data_year (DataYear): Tahun data untuk layer baru
        user (User): User yang membuat layer
        extraction_metadata (dict): Metadata about the extraction operation
        attribute_processor (callable): Function that processes attributes per feature.
            Takes feature.attributes as input, returns:
            - dict: Extracted attributes to store
            - None: Skip this feature

    Returns:
        dict: {
            'success': bool,
            'target_layer_id': int,
            'features_extracted': int,
            'message': str
        }
    """
    try:
        # 1. Cek apakah source layer ada
        try:
            source_layer = MasterLayer.objects.get(table_name=source_layer_name)
        except MasterLayer.DoesNotExist:
            return {
                'success': False,
                'message': f'Layer source "{source_layer_name}" tidak ditemukan'
            }

        # 2. Cek apakah target layer sudah ada
        if MasterLayer.objects.filter(table_name=target_layer_name).exists():
            return {
                'success': False,
                'message': f'Layer target "{target_layer_name}" sudah ada. Gunakan nama lain.'
            }

        # 3. Tentukan layer type dari source
        layer_type = source_layer.layer_type

        # 4. Buat MasterLayer baru
        with transaction.atomic():
            target_layer = MasterLayer.objects.create(
                name=target_layer_name.replace('_', ' ').title(),
                table_name=target_layer_name,
                layer_type=layer_type,
                layer_category=layer_category,
                data_year=data_year,
                created_by=user,
                attributes=extraction_metadata,
                is_active=True
            )

            logger.info(f"Created new layer: {target_layer_name}")

            # 5. Ekstrak fitur dari source layer
            source_features = FeatureData.objects.filter(layer=source_layer)
            features_count = 0

            for feature in source_features:
                # Ambil geometri
                geometry = feature.geometry

                # Proses atribut menggunakan callable
                extracted_attrs = attribute_processor(feature.attributes)

                # Skip jika attribute_processor mengembalikan None
                if extracted_attrs is None:
                    logger.warning(
                        f"Feature {feature.id} skipped: no matching attributes"
                    )
                    continue

                # Buat fitur baru dengan atribut yang diekstrak
                FeatureData.objects.create(
                    layer=target_layer,
                    geometry=geometry,
                    attributes=extracted_attrs
                )
                features_count += 1

            logger.info(f"Extracted {features_count} features to {target_layer_name}")

            return {
                'success': True,
                'target_layer_id': target_layer.id,
                'features_extracted': features_count,
                'message': f'Berhasil mengekstrak {features_count} fitur dari {source_layer_name} ke {target_layer_name}'
            }

    except Exception as e:
        logger.error(f"Error extracting layer: {str(e)}")
        return {
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }


def extract_layer_attribute(
    source_layer_name,
    target_layer_name,
    attribute_name,
    target_attribute_name=None,
    layer_category='tanah',
    data_year=None,
    user=None
):
    """
    Mengekstrak satu atribut dari layer source dan membuat layer baru.

    Args:
        source_layer_name (str): Nama layer source (contoh: 'unit_lahan')
        target_layer_name (str): Nama layer target baru (contoh: 'kalium')
        attribute_name (str): Nama atribut yang akan diekstrak (contoh: 'K_NILAI')
        target_attribute_name (str, optional): Nama atribut di layer target.
                                               Jika None, gunakan attribute_name
        layer_category (str): Kategori layer ('tanah', 'komoditas', 'lainnya')
        data_year (DataYear, optional): Tahun data untuk layer baru
        user (User, optional): User yang membuat layer

    Returns:
        dict: {
            'success': bool,
            'target_layer_id': int,
            'features_extracted': int,
            'message': str
        }

    Example:
        >>> result = extract_layer_attribute(
        ...     source_layer_name='unit_lahan',
        ...     target_layer_name='kalium',
        ...     attribute_name='K_NILAI',
        ...     target_attribute_name='nilai_k'
        ... )
    """
    # Validasi parameter
    if not target_attribute_name:
        target_attribute_name = attribute_name

    # Metadata untuk layer baru
    extraction_metadata = {
        'extracted_from': source_layer_name,
        'extracted_attribute': attribute_name,
        'extraction_type': 'single',
        'extraction_date': datetime.now().isoformat()
    }

    # Attribute processor untuk single attribute
    def process_attributes(feature_attrs):
        """Extract single attribute from feature"""
        if attribute_name not in feature_attrs:
            return None  # Skip feature
        return {target_attribute_name: feature_attrs[attribute_name]}

    return _create_extracted_layer(
        source_layer_name=source_layer_name,
        target_layer_name=target_layer_name,
        layer_category=layer_category,
        data_year=data_year,
        user=user,
        extraction_metadata=extraction_metadata,
        attribute_processor=process_attributes
    )


def extract_multiple_attributes(
    source_layer_name,
    target_layer_name,
    attribute_names,
    layer_category='tanah',
    data_year=None,
    user=None
):
    """
    Mengekstrak multiple atribut dari layer source dan membuat layer baru.

    Args:
        source_layer_name (str): Nama layer source
        target_layer_name (str): Nama layer target baru
        attribute_names (list): List nama atribut yang akan diekstrak
                                (contoh: ['K_NILAI', 'CORG_NILAI', 'PH_NILAI'])
        layer_category (str): Kategori layer
        data_year (DataYear, optional): Tahun data
        user (User, optional): User yang membuat layer

    Returns:
        dict: Result dengan status dan info

    Example:
        >>> result = extract_multiple_attributes(
        ...     source_layer_name='unit_lahan',
        ...     target_layer_name='karakteristik_tanah',
        ...     attribute_names=['K_NILAI', 'CORG_NILAI', 'PH_NILAI']
        ... )
    """
    # Validasi
    if not isinstance(attribute_names, list) or len(attribute_names) == 0:
        return {
            'success': False,
            'message': 'attribute_names harus berupa list dengan minimal 1 elemen'
        }

    # Metadata untuk layer baru
    extraction_metadata = {
        'extracted_from': source_layer_name,
        'extracted_attributes': attribute_names,
        'extraction_type': 'multiple',
        'extraction_date': datetime.now().isoformat()
    }

    # Attribute processor untuk multiple attributes
    def process_attributes(feature_attrs):
        """Extract multiple attributes from feature"""
        extracted = {
            attr: feature_attrs[attr]
            for attr in attribute_names
            if attr in feature_attrs
        }
        return extracted if extracted else None  # Skip jika tidak ada atribut

    result = _create_extracted_layer(
        source_layer_name=source_layer_name,
        target_layer_name=target_layer_name,
        layer_category=layer_category,
        data_year=data_year,
        user=user,
        extraction_metadata=extraction_metadata,
        attribute_processor=process_attributes
    )

    # Tambahkan attributes_extracted ke result untuk multiple
    if result['success']:
        result['attributes_extracted'] = attribute_names
        result['message'] = (
            f'Berhasil mengekstrak {result["features_extracted"]} fitur '
            f'dengan {len(attribute_names)} atribut'
        )

    return result


def list_layer_attributes(layer_name):
    """
    Mendapatkan daftar semua atribut yang ada di sebuah layer.

    Args:
        layer_name (str): Nama layer/table

    Returns:
        dict: {
            'success': bool,
            'layer_name': str,
            'attributes': list,
            'sample_values': dict
        }
    """
    try:
        layer = MasterLayer.objects.get(table_name=layer_name)
        features = FeatureData.objects.filter(layer=layer)

        if not features.exists():
            return {
                'success': False,
                'message': f'Layer "{layer_name}" tidak memiliki fitur'
            }

        # Ambil semua atribut unik dari semua fitur
        all_attributes = set()
        sample_values = {}

        for feature in features[:10]:  # Sample 10 fitur pertama
            for attr_name, attr_value in feature.attributes.items():
                all_attributes.add(attr_name)
                if attr_name not in sample_values:
                    sample_values[attr_name] = attr_value

        return {
            'success': True,
            'layer_name': layer_name,
            'layer_id': layer.id,
            'total_features': features.count(),
            'attributes': sorted(list(all_attributes)),
            'sample_values': sample_values
        }

    except MasterLayer.DoesNotExist:
        return {
            'success': False,
            'message': f'Layer "{layer_name}" tidak ditemukan'
        }
    except Exception as e:
        logger.error(f"Error listing attributes: {str(e)}")
        return {
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }


def batch_extract_attributes(extraction_configs):
    """
    Batch extraction untuk multiple layer target dari satu atau lebih source.

    Args:
        extraction_configs (list): List of dict dengan format:
            {
                'source_layer': str,
                'target_layer': str,
                'attributes': list or str,
                'target_attribute_name': str (optional, untuk single attribute)
            }

    Returns:
        dict: {
            'success': bool,
            'total_processed': int,
            'successful': list,
            'failed': list
        }
    """
    results = {
        'success': True,
        'total_processed': len(extraction_configs),
        'successful': [],
        'failed': []
    }

    for config in extraction_configs:
        source = config.get('source_layer')
        target = config.get('target_layer')
        attributes = config.get('attributes')

        if not source or not target or not attributes:
            results['failed'].append({
                'config': config,
                'error': 'Missing required parameters'
            })
            continue

        try:
            if isinstance(attributes, str):
                # Single attribute extraction
                result = extract_layer_attribute(
                    source_layer_name=source,
                    target_layer_name=target,
                    attribute_name=attributes,
                    target_attribute_name=config.get('target_attribute_name')
                )
            elif isinstance(attributes, list):
                # Multiple attributes extraction
                result = extract_multiple_attributes(
                    source_layer_name=source,
                    target_layer_name=target,
                    attribute_names=attributes
                )
            else:
                raise ValueError('attributes must be string or list')

            if result['success']:
                results['successful'].append({
                    'config': config,
                    'result': result
                })
            else:
                results['failed'].append({
                    'config': config,
                    'error': result['message']
                })

        except Exception as e:
            results['failed'].append({
                'config': config,
                'error': str(e)
            })

    results['success'] = len(results['failed']) == 0

    return results
