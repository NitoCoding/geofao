"""
Analysis Views Package

Re-exports all views for backward compatibility.
"""

from .result import (
    results_management,
    results_panel,
    toggle_result,
    results_geojson,
    api_results_geojson,
    result_detail,
)

from .control import (
    control_center,
    task_monitoring,
    batch_extract_ui,
    batch_overlay_ui,
    start_analysis_form,
    start_analysis_api,
    analysis_status_api,
    execute_batch_extract,
    execute_batch_overlay,
    delete_analysis,
)

__all__ = [
    # Management
    'results_management',
    'results_panel',
    'toggle_result',
    'results_geojson',
    'api_results_geojson',
    'result_detail',
    # Control
    'control_center',
    'task_monitoring',
    'batch_extract_ui',
    'batch_overlay_ui',
    'start_analysis_form',
    'start_analysis_api',
    'analysis_status_api',
    'execute_batch_extract',
    'execute_batch_overlay',
    'delete_analysis',
]
