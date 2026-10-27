# core/templatetags/table_tags.py
from django import template
register = template.Library()

@register.filter
def resolve(obj, path):
    """user|resolve:"profile.nama" -> memanggil callable otomatis"""
    for part in path.split("."):
        obj = getattr(obj, part, None)
        if callable(obj):
            obj = obj()
    return obj

@register.filter
def get_item(mapping, key):
    return mapping.get(key, "")

@register.filter
def lookup(d, key):
    return d.get(key) if d else None

@register.simple_tag(takes_context=True)
def qs(context, **overrides):
    params = context["request"].GET.copy()
    for k, v in overrides.items():
        params[k] = v
    return params.urlencode()

@register.simple_tag(takes_context=True)
def sort_url(context, key):
    """Siklus klik: asc -> desc -> tanpa sort. Filter tetap ikut, page di-reset."""
    params = context["request"].GET.copy()
    current = params.get("sort", "")

    if current == key:
        new = f"-{key}"
    elif current == f"-{key}":
        new = None
    else:
        new = key

    params.pop("page", None)
    if new:
        params["sort"] = new
    else:
        params.pop("sort", None)
    return "?" + params.urlencode()


@register.simple_tag
def sort_icon(key, current):
    if current == key:
        return "bi-arrow-up text-primary"
    if current == f"-{key}":
        return "bi-arrow-down text-primary"
    return "bi-chevron-expand opacity-30"


from django.urls import reverse

@register.simple_tag(takes_context=True)
def row_actions(context, col, obj):
    user = context["request"].user
    result = []
    for a in col.actions:
        if a.perm and not user.has_perm(a.perm):
            continue
        if a.show_if and not a.show_if(obj):
            continue
        result.append({
            "action": a,
            "url": reverse(a.url_name, args=[obj.pk]),
            "name": resolve(obj, a.name_attr) if a.name_attr else "",
        })
    return result