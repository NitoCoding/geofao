"""
Analysis URL Configuration

Routes untuk analisis kesesuaian lahan dengan Celery async processing.
"""

from django.urls import path
from .views import land_suitability, start_analysis, check_status, api_results_geojson
from .views_management import (
    results_management,
    results_panel,
    toggle_result,
    results_geojson,
)
from .control_views import (
    control_center,
    task_monitoring,
    batch_extract_ui,
    batch_overlay_ui,
    suitability_ui,
    start_analysis_form,
    start_analysis_api,
    analysis_status_api,
    execute_batch_extract,
    execute_batch_overlay,
    delete_analysis,
)

app_name = 'analysis'

urlpatterns = [
    # Main page - form untuk pilih komoditas dan layer
    path('kesesuaian-lahan/', land_suitability, name='land_suitability'),
    
    # HTMX endpoint - start analysis (trigger Celery task)
    path('kesesuaian-lahan/start/', start_analysis, name='start_analysis'),
    
    # HTMX polling endpoint - check status
    path('kesesuaian-lahan/status/<int:result_id>/', check_status, name='check_status'),

    # Control Center
    path('control/', control_center, name='control_center'),
    path('control/monitoring/', task_monitoring, name='task_monitoring'),
    path('control/batch-extract/', batch_extract_ui, name='batch_extract_ui'),
    path('control/batch-overlay/', batch_overlay_ui, name='batch_overlay_ui'),
    path('control/suitability/', suitability_ui, name='suitability_ui'),
    path('control/start-analysis/', start_analysis_form, name='start_analysis_form'),
    path('control/start-analysis/api/', start_analysis_api, name='start_analysis_api'),
    
    # API Endpoints
    path('control/status/', analysis_status_api, name='analysis_status_api'),
    path('control/status/<int:result_id>/', analysis_status_api, name='analysis_status_detail'),
    path('control/execute-batch-extract/', execute_batch_extract, name='execute_batch_extract'),
    path('control/execute-batch-overlay/', execute_batch_overlay, name='execute_batch_overlay'),
    path('control/delete/<int:result_id>/', delete_analysis, name='delete_analysis'),

    # GeoJSON API untuk hasil analisis
    path('api/results-geojson/', api_results_geojson, name='api_results_geojson'),
    path('api/results-geojson/<int:result_id>/', api_results_geojson, name='api_result_detail_geojson'),

    # Hasil Analisis Management (2-panel: list + map)
    path('results/', results_management, name='results_management'),
    path('results/panel/', results_panel, name='results_panel'),
    path('results/toggle/<int:result_id>/', toggle_result, name='toggle_result'),
    path('results/geojson/<int:result_id>/', results_geojson, name='results_geojson'),
]
