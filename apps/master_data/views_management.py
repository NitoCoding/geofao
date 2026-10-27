"""
Single-page Master Data Management View.

Satu halaman dengan 2 panel:
- Panel kiri: Grup Komoditas + Komoditas
- Panel kanan: Kriteria Kesesuaian

Add/Edit via modal HTMX, bukan full page form.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from apps.master_data.models import CommodityGroup, Commodity, DataYear, SuitabilityCharacteristic
from apps.master_data.forms import (
    CommodityGroupForm,
    CommodityForm,
    DataYearForm,
    SuitabilityCharacteristicForm,
)


# ================================================================
# MAIN PAGE
# ================================================================

class MasterDataManagementView(LoginRequiredMixin, View):
    """Halaman utama Master Data Management (2 panel)."""

    def get(self, request):
        groups = CommodityGroup.objects.all().order_by("order", "name")
        commodities = Commodity.objects.select_related("group").all().order_by("group__order", "name")
        criteria = SuitabilityCharacteristic.objects.select_related("commodity").all().order_by("commodity__name", "name")

        return render(request, "master_data/management/index.html", {
            "groups": groups,
            "commodities": commodities,
            "criteria": criteria,
            "all_commodities": Commodity.objects.all().order_by("name"),
        })


# ================================================================
# HTMX PARTIALS — LEFT PANEL
# ================================================================

@login_required
def left_panel(request):
    """Return panel kiri (grup + komoditas)."""
    groups = CommodityGroup.objects.all().order_by("order", "name")
    commodities = Commodity.objects.select_related("group").all().order_by("group__order", "name")
    return render(request, "master_data/management/_left_panel.html", {
        "groups": groups,
        "commodities": commodities,
    })


# ================================================================
# HTMX PARTIALS — RIGHT PANEL
# ================================================================

@login_required
def right_panel(request):
    """Return panel kanan (kriteria), optional filter by commodity."""
    commodity_id = request.GET.get("commodity")
    criteria = SuitabilityCharacteristic.objects.select_related("commodity").all()
    if commodity_id:
        criteria = criteria.filter(commodity_id=commodity_id)
    criteria = criteria.order_by("commodity__name", "name")

    return render(request, "master_data/management/_right_panel.html", {
        "criteria": criteria,
        "all_commodities": Commodity.objects.all().order_by("name"),
        "selected_commodity": commodity_id,
    })


# ================================================================
# HTMX MODAL FORMS — GROUP
# ================================================================

@login_required
def group_modal(request):
    """Return modal form untuk create/edit grup."""
    pk = request.GET.get("pk")
    instance = get_object_or_404(CommodityGroup, pk=pk) if pk else None
    form = CommodityGroupForm(instance=instance)
    return render(request, "master_data/management/_group_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST"])
def group_save(request):
    """Simpan grup (create/edit) via HTMX."""
    pk = request.POST.get("pk")
    instance = get_object_or_404(CommodityGroup, pk=pk) if pk else None
    form = CommodityGroupForm(request.POST, instance=instance)

    if form.is_valid():
        form.save()
        # Return left panel refreshed
        return left_panel(request)

    # Return modal form with errors
    return render(request, "master_data/management/_group_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def group_delete(request, pk):
    """Hapus grup via HTMX."""
    group = get_object_or_404(CommodityGroup, pk=pk)
    group.delete()
    return left_panel(request)


# ================================================================
# HTMX MODAL FORMS — COMMODITY
# ================================================================

@login_required
def commodity_modal(request):
    """Return modal form untuk create/edit komoditas."""
    pk = request.GET.get("pk")
    instance = get_object_or_404(Commodity, pk=pk) if pk else None
    form = CommodityForm(instance=instance)
    return render(request, "master_data/management/_commodity_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST"])
def commodity_save(request):
    """Simpan komoditas (create/edit) via HTMX."""
    pk = request.POST.get("pk")
    instance = get_object_or_404(Commodity, pk=pk) if pk else None
    form = CommodityForm(request.POST, instance=instance)

    if form.is_valid():
        form.save()
        return left_panel(request)

    return render(request, "master_data/management/_commodity_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def commodity_delete(request, pk):
    """Hapus komoditas via HTMX."""
    commodity = get_object_or_404(Commodity, pk=pk)
    commodity.delete()
    return left_panel(request)


# ================================================================
# HTMX MODAL FORMS — CRITERIA
# ================================================================

@login_required
def criteria_modal(request):
    """Return modal form untuk create/edit kriteria."""
    pk = request.GET.get("pk")
    instance = get_object_or_404(SuitabilityCharacteristic, pk=pk) if pk else None
    form = SuitabilityCharacteristicForm(instance=instance)
    return render(request, "master_data/management/_criteria_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST"])
def criteria_save(request):
    """Simpan kriteria (create/edit) via HTMX."""
    pk = request.POST.get("pk")
    instance = get_object_or_404(SuitabilityCharacteristic, pk=pk) if pk else None
    form = SuitabilityCharacteristicForm(request.POST, instance=instance)

    if form.is_valid():
        form.save()
        return right_panel(request)

    return render(request, "master_data/management/_criteria_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def criteria_delete(request, pk):
    """Hapus kriteria via HTMX."""
    criteria = get_object_or_404(SuitabilityCharacteristic, pk=pk)
    criteria.delete()
    return right_panel(request)


# ================================================================
# FULL PAGE — DATA YEAR
# ================================================================

class DataYearManagementView(LoginRequiredMixin, View):
    """Halaman standalone manajemen Tahun Data."""

    def get(self, request):
        data_years = DataYear.objects.all().order_by("-year")
        total_years = DataYear.objects.count()
        active_year = DataYear.objects.filter(is_active=True).first()
        return render(request, "master_data/management/data_year_management.html", {
            "data_years": data_years,
            "total_years": total_years,
            "active_year": active_year,
        })


# ================================================================
# HTMX PARTIALS — DATA YEAR
# ================================================================

@login_required
def data_year_panel(request):
    """Return panel tahun data (list + form)."""
    data_years = DataYear.objects.all().order_by("-year")
    return render(request, "master_data/management/_data_year_panel.html", {
        "data_years": data_years,
    })


@login_required
def data_year_modal(request):
    """Return modal form untuk create/edit tahun data."""
    pk = request.GET.get("pk")
    instance = get_object_or_404(DataYear, pk=pk) if pk else None
    form = DataYearForm(instance=instance)
    return render(request, "master_data/management/_data_year_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST"])
def data_year_save(request):
    """Simpan tahun data (create/edit) via HTMX."""
    pk = request.POST.get("pk")
    instance = get_object_or_404(DataYear, pk=pk) if pk else None
    form = DataYearForm(request.POST, instance=instance)

    if form.is_valid():
        form.save()
        return data_year_panel(request)

    return render(request, "master_data/management/_data_year_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def data_year_delete(request, pk):
    """Hapus tahun data via HTMX."""
    data_year = get_object_or_404(DataYear, pk=pk)
    data_year.delete()
    return data_year_panel(request)