"""
Analysis URL Configuration

Routes untuk analisis kesesuaian lahan dengan Celery async processing.
"""

from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # Control Center
    path('control/', views.control_center, name='control_center'),
    path('control/monitoring/', views.task_monitoring, name='task_monitoring'),
    path('control/batch-extract/', views.batch_extract_ui, name='batch_extract_ui'),
    path('control/batch-overlay/', views.batch_overlay_ui, name='batch_overlay_ui'),
    path('control/suitability/', views.suitability_ui, name='suitability_ui'),
    path('control/start-analysis/', views.start_analysis_form, name='start_analysis_form'),
    path('control/start-analysis/api/', views.start_analysis_api, name='start_analysis_api'),
    
    # API Endpoints
    path('control/status/', views.analysis_status_api, name='analysis_status_api'),
    path('control/status/<int:result_id>/', views.analysis_status_api, name='analysis_status_detail'),
    path('control/execute-batch-extract/', views.execute_batch_extract, name='execute_batch_extract'),
    path('control/execute-batch-overlay/', views.execute_batch_overlay, name='execute_batch_overlay'),
    path('control/delete/<int:result_id>/', views.delete_analysis, name='delete_analysis'),

    # GeoJSON API untuk hasil analisis
    path('api/results-geojson/', views.api_results_geojson, name='api_results_geojson'),
    path('api/results-geojson/<int:result_id>/', views.api_results_geojson, name='api_result_detail_geojson'),

    # Hasil Analisis Management (2-panel: list + map)
    path('results/', views.results_management, name='results_management'),
    path('results/panel/', views.results_panel, name='results_panel'),
    path('results/toggle/<int:result_id>/', views.toggle_result, name='toggle_result'),
    path('results/geojson/<int:result_id>/', views.results_geojson, name='results_geojson'),
    path('results/detail/<int:result_id>/', views.result_detail, name='result_detail'),
]
