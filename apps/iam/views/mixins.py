from django.http import HttpResponse
from django.shortcuts import redirect


class HtmxModalFormMixin:
    """Create/Update khusus modal HTMX. Request non-HTMX dialihkan ke halaman list."""

    list_url = None
    trigger_event = None

    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get("HX-Request"):
            return redirect(self.list_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        response = HttpResponse()
        response["HX-Trigger"] = self.trigger_event
        return response


class HtmxDeleteMixin:
    """Delete via POST (hx-post). Mengirim HX-Trigger agar list ter-refresh."""

    list_url = None
    trigger_event = None
    http_method_names = ["post"]

    def form_valid(self, form):
        self.object.delete()
        if not self.request.headers.get("HX-Request"):
            return redirect(self.list_url)
        response = HttpResponse()
        response["HX-Trigger"] = self.trigger_event
        return response
