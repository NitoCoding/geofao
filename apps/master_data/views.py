from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.decorators.http import require_http_methods
from django_htmx.http import trigger_client_event

from apps.master_data.models import CommodityGroup, Commodity, DataYear, SuitabilityCharacteristic
from apps.master_data.forms import (
    CommodityGroupForm,
    CommodityForm,
    DataYearForm,
    SuitabilityCharacteristicForm,
)


# ================================================================
# SINGLE-PAGE MANAGEMENT (HTMX-based, 2-panel layout)
# ================================================================

class MasterDataManagementView(LoginRequiredMixin, View):
    """Halaman utama Master Data Management (2 panel)."""

    def get(self, request):
        groups = CommodityGroup.objects.all().order_by("order", "name")
        commodities = Commodity.objects.select_related("group").all().order_by("group__order", "name")
        criteria = SuitabilityCharacteristic.objects.none()

        return render(request, "master_data/commodity/index.html", {
            "groups": groups,
            "commodities": commodities,
            "criteria": criteria,
        })


# ================================================================
# HTMX PARTIALS — LEFT PANEL (Group + Commodity)
# ================================================================

@login_required
def left_panel(request):
    """Return panel kiri (grup + komoditas)."""
    groups = CommodityGroup.objects.all().order_by("order", "name")
    commodities = Commodity.objects.select_related("group").all().order_by("group__order", "name")
    return render(request, "master_data/commodity/partials/left_panel.html", {
        "groups": groups,
        "commodities": commodities,
    })


# ================================================================
# HTMX PARTIALS — RIGHT PANEL (Criteria)
# ================================================================

@login_required
def right_panel(request):
    """Return panel kanan (kriteria), filter by commodity."""
    commodity_id = request.GET.get("commodity")
    commodity_name = None
    if commodity_id:
        criteria = SuitabilityCharacteristic.objects.select_related("commodity").filter(
            commodity_id=commodity_id
        ).order_by("commodity__name", "name")
        try:
            commodity_name = criteria[0].commodity.name if criteria else Commodity.objects.get(pk=commodity_id).name
        except Commodity.DoesNotExist:
            commodity_name = None
    else:
        criteria = SuitabilityCharacteristic.objects.none()

    return render(request, "master_data/commodity/partials/right_panel.html", {
        "criteria": criteria,
        "commodity_id": commodity_id,
        "commodity_name": commodity_name,
    })


# ================================================================
# HTMX MODAL FORMS — GROUP
# ================================================================

@login_required
def group_modal(request, pk=None):
    """Return modal form untuk create/edit grup."""
    pk = pk or request.GET.get("pk")
    instance = get_object_or_404(CommodityGroup, pk=pk) if pk else None
    form = CommodityGroupForm(instance=instance)
    return render(request, "master_data/commodity/partials/group_modal.html", {
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
        response = HttpResponse(status=204)
        trigger_client_event(response, "modalClose")
        trigger_client_event(response, "groupChanged")
        return response

    return render(request, "master_data/commodity/partials/group_modal.html", {
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
def commodity_modal(request, pk=None):
    """Return modal form untuk create/edit komoditas."""
    pk = pk or request.GET.get("pk")
    instance = get_object_or_404(Commodity, pk=pk) if pk else None
    form = CommodityForm(instance=instance)
    return render(request, "master_data/commodity/partials/commodity_modal.html", {
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
        response = HttpResponse(status=204)
        trigger_client_event(response, "modalClose")
        trigger_client_event(response, "commodityChanged")
        return response

    return render(request, "master_data/commodity/partials/commodity_modal.html", {
        "form": form,
        "instance": instance,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def commodity_delete(request, pk):
    """Hapus komoditas via HTMX."""
    commodity = get_object_or_404(Commodity, pk=pk)
    commodity.delete()
    response = HttpResponse()
    trigger_client_event(response, "commodityChanged")
    trigger_client_event(response, "criteriaChanged")
    return response


# ================================================================
# HTMX MODAL FORMS — CRITERIA
# ================================================================

@login_required
@require_http_methods(["GET", "POST"])
def criteria_modal(request, pk=None):
    """Handle GET (show form) dan POST (save) untuk criteria modal."""
    commodity_id = request.GET.get("commodity")

    if request.method == "POST":
        instance = get_object_or_404(SuitabilityCharacteristic, pk=pk) if pk else None
        form = SuitabilityCharacteristicForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            trigger_client_event(response, "modalClose")
            trigger_client_event(response, "criteriaChanged")
            return response
    else:
        instance = get_object_or_404(SuitabilityCharacteristic, pk=pk) if pk else None
        initial = {}
        if commodity_id:
            initial["commodity"] = commodity_id
        form = SuitabilityCharacteristicForm(instance=instance, initial=initial)
        # print(form.fields["commodity"])

    return render(request, "master_data/commodity/partials/criteria_modal.html", {
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
# DATA YEAR MANAGEMENT
# ================================================================

class DataYearManagementView(LoginRequiredMixin, View):
    """Halaman standalone manajemen Tahun Data."""

    def get(self, request):
        data_years = DataYear.objects.all().order_by("-year")
        total_years = DataYear.objects.count()
        active_year = DataYear.objects.filter(is_active=True).first()
        return render(request, "master_data/year/index.html", {
            "data_years": data_years,
            "total_years": total_years,
            "active_year": active_year,
        })


@login_required
def data_year_panel(request):
    """Return panel tahun data (list + form)."""
    data_years = DataYear.objects.all().order_by("-year")
    return render(request, "master_data/year/partials/data_year_panel.html", {
        "data_years": data_years,
    })


@login_required
def data_year_modal(request, pk=None):
    """Return modal form untuk create/edit tahun data."""
    pk = pk or request.GET.get("pk")
    instance = get_object_or_404(DataYear, pk=pk) if pk else None
    form = DataYearForm(instance=instance)
    return render(request, "master_data/year/partials/data_year_modal.html", {
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
        response = HttpResponse(status=204)
        trigger_client_event(response, "modalClose")
        trigger_client_event(response, "dataYearChanged")
        return response

    return render(request, "master_data/year/partials/data_year_modal.html", {
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