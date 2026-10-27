# core/tables.py
from django.http import HttpResponse
from pyexpat.errors import messages
from dataclasses import dataclass
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

@dataclass
class Action:
    label: str                       # tooltip
    icon: str                        # class bootstrap-icons, contoh "bi-pencil"
    url_name: str                    # nama url, dipanggil reverse(url_name, args=[obj.pk])
    style: str = "btn-ghost"         # tulis class lengkap: "btn-error", "btn-primary", dst
    confirm: bool = False            # True -> buka modal konfirmasi (untuk hapus)
    hx_method: str | None = None     # tombol HTMX + hx-confirm
    hx_confirm: str = ""             # pesan konfirmasi HTMX
    modal: bool = False              # True -> buka modal (untuk edit)
    name_attr: str = ""              # atribut object yang ditampilkan di modal, contoh "username"
    perm: str | None = None          # permission Django, contoh "auth.delete_user"
    show_if: callable = None         # lambda obj: bool, contoh lambda obj: obj.is_active

@dataclass
class Column:
    key: str
    label: str
    attr: str | None = None
    filter: str | None = None      # None | "text" | "select" | "date"
    lookups: tuple = ()
    choices: tuple = ()
    coerce: callable = None
    badges: dict = None
    cell: str | None = None
    width: str = ""
    sort_fields: tuple = ()      # field ORM untuk order_by; kosong = tidak bisa di-sort
    actions: tuple = ()          # field ORM untuk actions; kosong = tidak bisa di-aksi

    @property
    def path(self):
        return self.attr or self.key

    def build_q(self, raw):
        if self.filter == "select" and raw not in dict(self.choices):
            return None
        value = self.coerce(raw) if self.coerce else raw
        q = Q()
        for lk in self.lookups:
            q |= Q(**{lk: value})
        return q or None

def apply_sort(qs, params, columns, default=None):
    """
    ?sort=email  -> ascending, ?sort=-email -> descending.
    Hanya key yang ada di columns (dan punya sort_fields) yang diterima.
    """
    raw = params.get("sort", "")
    key = raw.lstrip("-")
    col = next((c for c in columns if c.key == key and c.sort_fields), None)

    if col is None:
        return (qs.order_by(*default), "") if default else (qs, "")

    prefix = "-" if raw.startswith("-") else ""
    ordering = [f"{prefix}{f}" for f in col.sort_fields]
    ordering.append("pk")        # tie-breaker supaya urutan antar halaman stabil
    return qs.order_by(*ordering), raw

def apply_filters(qs, params, columns):
    """Terapkan filter dari request.GET sesuai definisi columns."""
    for col in columns:
        if not col.filter:
            continue
        raw = params.get(col.key, "").strip()
        if raw and (q := col.build_q(raw)) is not None:
            qs = qs.filter(q)
    return qs


def render_table(request, *, qs, columns, list_url, page_template,
                 row_actions_template, per_page=20, default_sort=None, extra=None):
    qs = apply_filters(qs, request.GET, columns)
    qs, sort = apply_sort(qs, request.GET, columns, default=default_sort)
    page_obj = Paginator(qs, per_page).get_page(request.GET.get("page"))

    ctx = {
        "columns": columns,
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "f": request.GET,
        "sort": sort,                         # <- baru
        "list_url": list_url,
        "row_actions_template": row_actions_template,
        "colspan": len(columns),
        "has_filter": any(k not in ("page", "sort") and v for k, v in request.GET.items()),
        **(extra or {}),
    }

    is_htmx = (request.headers.get("HX-Request")
               and not request.headers.get("HX-History-Restore-Request"))
    template = "components/_table_rows.html" if is_htmx else page_template
    return render(request, template, ctx)


from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render

def style_form(form):
    """Beri class DaisyUI ke widget supaya template form tetap generik."""
    for f in form.fields.values():
        w = f.widget
        if isinstance(w, forms.CheckboxInput):
            cls = "checkbox"
        elif isinstance(w, forms.Select):
            cls = "select select-bordered w-full"
        elif isinstance(w, forms.Textarea):
            cls = "textarea textarea-bordered w-full"
        else:
            cls = "input input-bordered w-full"
        w.attrs["class"] = f"{w.attrs.get('class', '')} {cls}".strip()
    return form


def modal_form(request, *, form_class, title, instance=None,
               success_message="Data berhasil disimpan.", extra=None):
    """GET -> render form. POST valid -> simpan + HX-Refresh. POST invalid -> render ulang."""
    form = style_form(form_class(request.POST or None, instance=instance))

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return HttpResponse(headers={"HX-Refresh": "true"})

    return render(request, "components/_modal_form.html",
                  {"form": form, "title": title, **(extra or {})})