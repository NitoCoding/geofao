from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from apps.master_data.forms import (
    CommodityForm,
    CommodityGroupForm,
    SuitabilityCharacteristicForm,
)
from apps.master_data.models import Commodity, CommodityGroup, SuitabilityCharacteristic


# Create your views here.
# --- VIEWS UNTUK COMMODITY GROUP ---
class CommodityGroupListView(LoginRequiredMixin, ListView):
    model = CommodityGroup
    template_name = "master_data/commoditygroup_list.html"
    context_object_name = "groups"
    paginate_by = 10


class CommodityGroupCreateView(LoginRequiredMixin, CreateView):
    model = CommodityGroup
    form_class = CommodityGroupForm
    template_name = "master_data/commoditygroup_form.html"
    success_url = reverse_lazy("master_data:commoditygroup_list")


class CommodityGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = CommodityGroup
    form_class = CommodityGroupForm
    template_name = "master_data/commoditygroup_form.html"
    success_url = reverse_lazy("master_data:commoditygroup_list")


class CommodityGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = CommodityGroup
    template_name = "master_data/commoditygroup_confirm_delete.html"
    success_url = reverse_lazy("master_data:commoditygroup_list")


# --- VIEWS UNTUK COMMODITY ---
class CommodityListView(LoginRequiredMixin, ListView):
    model = Commodity
    template_name = "master_data/commodity_list.html"
    context_object_name = "commodities"
    paginate_by = 10


class CommodityCreateView(LoginRequiredMixin, CreateView):
    model = Commodity
    form_class = CommodityForm
    template_name = "master_data/commodity_form.html"
    success_url = reverse_lazy("master_data:commodity_list")


class CommodityUpdateView(LoginRequiredMixin, UpdateView):
    model = Commodity
    form_class = CommodityForm
    template_name = "master_data/commodity_form.html"
    success_url = reverse_lazy("master_data:commodity_list")


class CommodityDeleteView(LoginRequiredMixin, DeleteView):
    model = Commodity
    template_name = "master_data/commodity_confirm_delete.html"
    success_url = reverse_lazy("master_data:commodity_list")


class SuitabilityCharacteristicCreateView(LoginRequiredMixin, CreateView):
    model = SuitabilityCharacteristic
    form_class = SuitabilityCharacteristicForm
    template_name = "master_data/suitabilitycharacteristic_form.html"
    success_url = reverse_lazy("master_data:suitabilitycharacteristic_list")


class SuitabilityCharacteristicUpdateView(LoginRequiredMixin, UpdateView):
    model = SuitabilityCharacteristic
    form_class = SuitabilityCharacteristicForm
    template_name = "master_data/suitabilitycharacteristic_form.html"
    success_url = reverse_lazy("master_data:suitabilitycharacteristic_list")


class SuitabilityCharacteristicListView(LoginRequiredMixin, ListView):
    model = SuitabilityCharacteristic
    template_name = "master_data/suitabilitycharacteristic_list.html"
    context_object_name = "criteria"
    paginate_by = 15

    def get_queryset(self):
        # Filter berdasarkan komoditas jika ada di URL
        queryset = super().get_queryset()
        commodity_id = self.request.GET.get("commodity")
        if commodity_id:
            queryset = queryset.filter(commodity_id=commodity_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commodities"] = Commodity.objects.all()
        context["selected_commodity"] = self.request.GET.get("commodity")
        return context


class SuitabilityCharacteristicDeleteView(LoginRequiredMixin, DeleteView):
    model = SuitabilityCharacteristic
    template_name = "master_data/suitabilitycharacteristic_confirm_delete.html"
    success_url = reverse_lazy("spatial:suitabilitycharacteristic_list")
