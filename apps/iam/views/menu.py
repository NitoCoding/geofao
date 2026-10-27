from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.iam.forms import MenuForm
from apps.iam.models import Menu
from apps.iam.views.mixins import HtmxModalFormMixin, HtmxDeleteMixin


class MenuListView(LoginRequiredMixin, ListView):
    model = Menu
    template_name = "iam/menus/index.html"
    context_object_name = "menus"
    paginate_by = 10

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/menus/datatable.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset().select_related("parent")
        request = self.request

        filters = {
            "filter_name": "name__icontains",
            "filter_code": "code__icontains",
            "filter_path": "path__icontains",
            "filter_parent": "parent__name__icontains",
            "filter_type": "menu_type",
            "filter_order": "order",
        }
        for param, lookup in filters.items():
            value = request.GET.get(param, "").strip()
            if param == "filter_order" and not value.isdigit():
                continue
            if value:
                qs = qs.filter(**{lookup: value})

        filter_status = request.GET.get("filter_status", "").strip()
        if filter_status == "active":
            qs = qs.filter(is_active=True)
        elif filter_status == "inactive":
            qs = qs.filter(is_active=False)

        return qs.order_by("parent__id", "order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["total_menus"] = Menu.objects.count()
        context["active_menus"] = Menu.objects.filter(is_active=True).count()
        context["parent_menus"] = Menu.objects.filter(menu_type="parent").count()

        for param in ["filter_name", "filter_code", "filter_path", "filter_parent",
                      "filter_type", "filter_order", "filter_status"]:
            context[param] = request.GET.get(param, "")
        context["menu_types"] = Menu.MENU_TYPES

        params = request.GET.copy()
        params.pop("page", None)
        context["filter_qs"] = urlencode(params)
        return context


class MenuCreateView(HtmxModalFormMixin, LoginRequiredMixin, CreateView):
    model = Menu
    form_class = MenuForm
    template_name = "iam/menus/_menu_modal.html"
    list_url = reverse_lazy("iam:menu_list")
    trigger_event = "menuSaved"


class MenuUpdateView(HtmxModalFormMixin, LoginRequiredMixin, UpdateView):
    model = Menu
    form_class = MenuForm
    template_name = "iam/menus/_menu_modal.html"
    list_url = reverse_lazy("iam:menu_list")
    trigger_event = "menuSaved"


class MenuDeleteView(HtmxDeleteMixin, LoginRequiredMixin, DeleteView):
    model = Menu
    list_url = reverse_lazy("iam:menu_list")
    trigger_event = "menuSaved"
