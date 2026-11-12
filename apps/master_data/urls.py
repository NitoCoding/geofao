from django.urls import path
from . import views

app_name = 'master_data'

urlpatterns = [
    # ===== SINGLE-PAGE MASTER DATA MANAGEMENT =====
    path('commodity-criteria', views.MasterDataManagementView.as_view(), name='management'),

    # Panel kiri & kanan (HTMX partial)
    path('_left/', views.left_panel, name='management_left'),
    path('_right/', views.right_panel, name='management_right'),

    # --- Grup Komoditas (CRUD via modal HTMX) ---
    path('_group/create/', views.group_modal, name='management_group_modal'),
    path('_group/<int:pk>/edit/', views.group_modal, name='management_group_modal'),
    path('_group/save/', views.group_save, name='management_group_save'),
    path('_group/<int:pk>/delete/', views.group_delete, name='management_group_delete'),

    # --- Komoditas (CRUD via modal HTMX) ---
    path('_commodity/create/', views.commodity_modal, name='management_commodity_modal'),
    path('_commodity/<int:pk>/edit/', views.commodity_modal, name='management_commodity_modal'),
    path('_commodity/save/', views.commodity_save, name='management_commodity_save'),
    path('_commodity/<int:pk>/delete/', views.commodity_delete, name='management_commodity_delete'),

    # --- Kriteria Kesesuaian (CRUD via modal HTMX) ---
    path('_criteria/create/', views.criteria_modal, name='management_criteria_modal'),
    path('_criteria/<int:pk>/edit/', views.criteria_modal, name='management_criteria_modal'),
    path('_criteria/<int:pk>/delete/', views.criteria_delete, name='management_criteria_delete'),

    # --- Tahun Data (halaman penuh + CRUD via modal HTMX) ---
    path('data-years/', views.DataYearManagementView.as_view(), name='management_data_year_page'),
    path('_data-year/', views.data_year_panel, name='management_data_year'),
    path('_data-year/create/', views.data_year_modal, name='management_data_year_modal'),
    path('_data-year/<int:pk>/edit/', views.data_year_modal, name='management_data_year_modal'),
    path('_data-year/save/', views.data_year_save, name='management_data_year_save'),
    path('_data-year/<int:pk>/delete/', views.data_year_delete, name='management_data_year_delete'),
]