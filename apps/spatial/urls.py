from django.urls import path
from . import views

app_name = 'spatial'

urlpatterns = [
    # Main Pages
    # path('', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map_view'),

    # Layer Management
    path('layers/', views.layer_management, name='layer_management'),
    path('layers/table/', views.layer_list_table, name='layer_list_table'),
    path('layers/upload/', views.layer_upload, name='layer_upload'),
    path('layers/upload-modal/', views.layer_upload_modal, name='layer_upload_modal'),
    path('layers/<int:pk>/', views.layer_detail, name='layer_detail'),
    path('layers/<int:pk>/toggle/', views.layer_toggle, name='layer_toggle'),
    path('layers/<int:pk>/edit/', views.layer_edit, name='layer_edit'),
    path('layers/<int:pk>/delete/', views.layer_delete, name='layer_delete'),

    # API Endpoints
    path('api/layers/<int:pk>/geojson/', views.api_layer_geojson, name='api_layer_geojson'),
    path('api/expert-reviews/', views.api_expert_reviews, name='api_expert_reviews'),
    path('spatial/api/feature-at-point/', views.api_feature_at_point, name='api_feature_at_point'),
    path('spatial/api/feature-at-point-htmx/', views.api_feature_at_point_htmx, name='api_feature_at_point_htmx'),

    # API Endpoints for Categories
    path('api/land-categories/', views.api_land_categories, name='api_land_categories'),
    path('api/commodity-categories/', views.api_commodity_categories, name='api_commodity_categories'),
    path('api/commodities/by-category/<str:category_type>/', views.api_commodities_by_category, name='api_commodities_by_category'),

    # Layer Extraction API
    path('api/layer/extract/', views.api_extract_layer_attribute, name='api_extract_layer_attribute'),
    path('api/layer/batch-extract/', views.api_batch_extract_layers, name='api_batch_extract_layers'),

    # Layer Overlay API
    path('api/layer/overlay/', views.api_overlay_layers, name='api_overlay_layers'),
    path('api/layer/<int:layer_id>/statistics/', views.api_layer_statistics, name='api_layer_statistics'),

    # Active Data Year
    path('set-data-year/<int:year_id>/', views.set_active_data_year, name='set_data_year'),

    # Master Data Home




]