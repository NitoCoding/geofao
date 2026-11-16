from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.iam.forms import MenuRoleForm
from apps.iam.models import MenuRole, Role
from apps.iam.views.mixins import HtmxModalFormMixin, HtmxDeleteMixin


class MenuRoleListView(LoginRequiredMixin, ListView):
    model = MenuRole
    template_name = "iam/menu_roles/index.html"
    context_object_name = "menu_roles"
    paginate_by = 10

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/menu_roles/datatable.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset().select_related("menu", "role")
        request = self.request

        filter_menu = request.GET.get("filter_menu", "").strip()
        if filter_menu:
            qs = qs.filter(menu__name__icontains=filter_menu)

        filter_role = request.GET.get("filter_role", "").strip()
        if filter_role:
            qs = qs.filter(role__code=filter_role)

        return qs.order_by("menu__name", "role__name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["total_pairs"] = MenuRole.objects.count()
        context["linked_menus"] = MenuRole.objects.values("menu").distinct().count()
        context["linked_roles"] = MenuRole.objects.values("role").distinct().count()

        context["filter_menu"] = request.GET.get("filter_menu", "")
        context["filter_role"] = request.GET.get("filter_role", "")
        context["available_roles"] = Role.objects.filter(is_active=True).order_by("code")

        params = request.GET.copy()
        params.pop("page", None)
        context["filter_qs"] = urlencode(params)
        return context


class MenuRoleCreateView(HtmxModalFormMixin, LoginRequiredMixin, CreateView):
    model = MenuRole
    form_class = MenuRoleForm
    template_name = "iam/menu_roles/_menu_role_modal.html"
    list_url = reverse_lazy("iam:menu_role_list")
    trigger_event = "menuRoleSaved, modalClose"


class MenuRoleUpdateView(HtmxModalFormMixin, LoginRequiredMixin, UpdateView):
    model = MenuRole
    form_class = MenuRoleForm
    template_name = "iam/menu_roles/_menu_role_modal.html"
    list_url = reverse_lazy("iam:menu_role_list")
    trigger_event = "menuRoleSaved, modalClose"


class MenuRoleDeleteView(HtmxDeleteMixin, LoginRequiredMixin, DeleteView):
    model = MenuRole
    list_url = reverse_lazy("iam:menu_role_list")
    trigger_event = "menuRoleSaved"
