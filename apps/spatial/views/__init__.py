"""
Spatial Views Package

Re-exports all views for backward compatibility.
This allows urls.py to continue using `from . import views` without changes.
"""

# Layer CRUD Views
from .layer_views import (
    layer_management,
    layer_list,
    layer_list_table,
    layer_upload,
    layer_upload_modal,
    layer_detail,
    layer_toggle,
    layer_edit,
    layer_delete,
)

# Map and GeoJSON Views
from .map_views import (
    map_view,
    api_layer_geojson,
    api_feature_at_point,
    api_feature_at_point_htmx,
    api_expert_reviews,
)

# Category API Views
from .api_views import (
    api_land_categories,
    api_commodity_categories,
    api_commodities_by_category,
)

# Layer Extraction Views
from .extraction_views import (
    api_extract_layer_attribute,
    api_batch_extract_layers,
)

# Layer Overlay Views
from .overlay_views import (
    api_overlay_layers,
    api_layer_statistics,
)

# Admin Views
from .admin_views import (
    set_active_data_year,
)

# Make all views available at package level
__all__ = [
    # Layer CRUD
    'layer_management',
    'layer_list',
    'layer_list_table',
    'layer_upload',
    'layer_upload_modal',
    'layer_detail',
    'layer_toggle',
    'layer_edit',
    'layer_delete',
    # Map and GeoJSON
    'map_view',
    'api_layer_geojson',
    'api_feature_at_point',
    'api_feature_at_point_htmx',
    'api_expert_reviews',
    # Category API
    'api_land_categories',
    'api_commodity_categories',
    'api_commodities_by_category',
    # Extraction
    'api_extract_layer_attribute',
    'api_batch_extract_layers',
    # Overlay
    'api_overlay_layers',
    'api_layer_statistics',
    # Admin
    'set_active_data_year',
]
