from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from apps.iam.models import User, Role
from apps.iam.forms import UserForm
from apps.iam.views.mixins import HtmxDeleteMixin


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "iam/users/index.html"
    context_object_name = "users"
    paginate_by = 10

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/users/datatable.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        # Global search
        search = request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        # Per-column filters
        filter_username = request.GET.get("filter_username", "").strip()
        if filter_username:
            qs = qs.filter(username__icontains=filter_username)

        filter_email = request.GET.get("filter_email", "").strip()
        if filter_email:
            qs = qs.filter(email__icontains=filter_email)

        filter_nama = request.GET.get("filter_nama", "").strip()
        if filter_nama:
            qs = qs.filter(
                Q(first_name__icontains=filter_nama)
                | Q(last_name__icontains=filter_nama)
            )

        filter_status = request.GET.get("filter_status", "").strip()
        if filter_status == "active":
            qs = qs.filter(is_active=True)
        elif filter_status == "inactive":
            qs = qs.filter(is_active=False)

        filter_role = request.GET.get("filter_role", "").strip()
        if filter_role:
            qs = qs.filter(roles__code=filter_role).distinct()

        return qs.order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["total_users"] = User.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        context["admin_users"] = User.objects.filter(roles__code="admin").count()
        context["expert_users"] = User.objects.filter(roles__code="tenaga_ahli").count()

        # Search & filter values for form persistence
        context["search_query"] = request.GET.get("q", "")
        context["filter_username"] = request.GET.get("filter_username", "")
        context["filter_email"] = request.GET.get("filter_email", "")
        context["filter_nama"] = request.GET.get("filter_nama", "")
        context["filter_status"] = request.GET.get("filter_status", "")
        context["filter_role"] = request.GET.get("filter_role", "")

        # Available roles for filter dropdown
        context["available_roles"] = Role.objects.filter(is_active=True).order_by("code")

        # Build query string for pagination (exclude 'page')
        params = request.GET.copy()
        params.pop("page", None)
        context["filter_qs"] = urlencode(params)

        return context


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy("iam:user_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/users/_user_modal.html"]
        return ["iam/users/form.html"]

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Trigger"] = "userSaved"
            return response
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy("iam:user_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["iam/users/_user_modal.html"]
        return ["iam/users/form.html"]

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Trigger"] = "userSaved"
            return response
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)


class UserDeleteView(HtmxDeleteMixin, LoginRequiredMixin, DeleteView):
    model = User
    list_url = reverse_lazy("iam:user_list")
    trigger_event = "userSaved"