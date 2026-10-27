from django.urls import path
from . import views
from . import views_management

app_name = 'master_data'

urlpatterns = [
    # ===== SINGLE-PAGE MASTER DATA MANAGEMENT =====
    path('commodity-criteria/', views_management.MasterDataManagementView.as_view(), name='management'),

    # Panel kiri & kanan (HTMX partial)
    path('_left/', views_management.left_panel, name='management_left'),
    path('_right/', views_management.right_panel, name='management_right'),

    # --- Grup Komoditas (CRUD via modal HTMX) ---
    path('_group/modal/', views_management.group_modal, name='management_group_modal'),
    path('_group/save/', views_management.group_save, name='management_group_save'),
    path('_group/<int:pk>/delete/', views_management.group_delete, name='management_group_delete'),

    # --- Komoditas (CRUD via modal HTMX) ---
    path('_commodity/modal/', views_management.commodity_modal, name='management_commodity_modal'),
    path('_commodity/save/', views_management.commodity_save, name='management_commodity_save'),
    path('_commodity/<int:pk>/delete/', views_management.commodity_delete, name='management_commodity_delete'),

    # --- Kriteria Kesesuaian (CRUD via modal HTMX) ---
    path('_criteria/modal/', views_management.criteria_modal, name='management_criteria_modal'),
    path('_criteria/save/', views_management.criteria_save, name='management_criteria_save'),
    path('_criteria/<int:pk>/delete/', views_management.criteria_delete, name='management_criteria_delete'),

    # --- Tahun Data (halaman penuh + CRUD via modal HTMX) ---
    path('data-years/', views_management.DataYearManagementView.as_view(), name='management_data_year_page'),
    path('_data-year/', views_management.data_year_panel, name='management_data_year'),
    path('_data-year/modal/', views_management.data_year_modal, name='management_data_year_modal'),
    path('_data-year/save/', views_management.data_year_save, name='management_data_year_save'),
    path('_data-year/<int:pk>/delete/', views_management.data_year_delete, name='management_data_year_delete'),

    # ===== LEGACY (tetap tersedia) =====
    # Commodity Group URLs
    path('commodity-groups/', views.CommodityGroupListView.as_view(), name='commoditygroup_list'),
    path('commodity-groups/create/', views.CommodityGroupCreateView.as_view(), name='commoditygroup_create'),
    path('commodity-groups/<int:pk>/edit/', views.CommodityGroupUpdateView.as_view(), name='commoditygroup_edit'),
    path('commodity-groups/<int:pk>/delete/', views.CommodityGroupDeleteView.as_view(), name='commoditygroup_delete'),

    # Commodity URLs
    path('commodities/', views.CommodityListView.as_view(), name='commodity_list'),
    path('commodities/create/', views.CommodityCreateView.as_view(), name='commodity_create'),
    path('commodities/<int:pk>/edit/', views.CommodityUpdateView.as_view(), name='commodity_edit'),
    path('commodities/<int:pk>/delete/', views.CommodityDeleteView.as_view(), name='commodity_delete'),

    # Suitability Characteristic URLs
    path('criteria/', views.SuitabilityCharacteristicListView.as_view(), name='suitabilitycharacteristic_list'),
    path('criteria/create/', views.SuitabilityCharacteristicCreateView.as_view(), name='suitabilitycharacteristic_create'),
    path('criteria/<int:pk>/edit/', views.SuitabilityCharacteristicUpdateView.as_view(), name='suitabilitycharacteristic_edit'),
    path('criteria/<int:pk>/delete/', views.SuitabilityCharacteristicDeleteView.as_view(), name='suitabilitycharacteristic_delete'),
]