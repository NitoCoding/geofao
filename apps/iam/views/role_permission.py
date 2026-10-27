from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from apps.iam.forms import RolePermissionForm
from apps.iam.models import Role
from apps.iam.views.mixins import HtmxModalFormMixin, HtmxDeleteMixin

RolePermission = Role.permissions.through


class RolePermissionListView(LoginRequiredMixin, ListView):
    model = RolePermission
    template_name = "iam/role_permissions/index.html"
    context_object_name = "role_permissions"
    paginate_by = 10

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/role_permissions/datatable.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset().select_related("role", "permission__content_type")
        request = self.request

        filter_role = request.GET.get("filter_role", "").strip()
        if filter_role:
            qs = qs.filter(role__code=filter_role)

        filter_app = request.GET.get("filter_app", "").strip()
        if filter_app:
            qs = qs.filter(permission__content_type__app_label__icontains=filter_app)

        filter_permission = request.GET.get("filter_permission", "").strip()
        if filter_permission:
            qs = qs.filter(permission__name__icontains=filter_permission)

        return qs.order_by("role__code", "permission__content_type__app_label", "permission__codename")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["total_pairs"] = RolePermission.objects.count()
        context["linked_roles"] = RolePermission.objects.values("role").distinct().count()
        context["linked_permissions"] = RolePermission.objects.values("permission").distinct().count()

        context["filter_role"] = request.GET.get("filter_role", "")
        context["filter_app"] = request.GET.get("filter_app", "")
        context["filter_permission"] = request.GET.get("filter_permission", "")
        context["available_roles"] = Role.objects.filter(is_active=True).order_by("code")

        params = request.GET.copy()
        params.pop("page", None)
        context["filter_qs"] = urlencode(params)
        return context


class RolePermissionCreateView(HtmxModalFormMixin, LoginRequiredMixin, CreateView):
    model = RolePermission
    form_class = RolePermissionForm
    template_name = "iam/role_permissions/_role_permission_modal.html"
    list_url = reverse_lazy("iam:role_permission_list")
    trigger_event = "rolePermissionSaved"


class RolePermissionDeleteView(HtmxDeleteMixin, LoginRequiredMixin, DeleteView):
    model = RolePermission
    list_url = reverse_lazy("iam:role_permission_list")
    trigger_event = "rolePermissionSaved"
