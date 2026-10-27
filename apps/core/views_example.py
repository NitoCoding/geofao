# iam/views.py
from apps.core.tables import Action
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from apps.core.tables import Column, render_table

User = get_user_model()

USER_COLUMNS = [
    Column("username", "Username", filter="text", lookups=("username__icontains",),
           sort_fields=("username",)),
    Column("email", "Email", filter="text", lookups=("email__icontains",),
           sort_fields=("email",)),
    Column("nama", "Nama", attr="get_full_name", filter="text",
           lookups=("first_name__icontains", "last_name__icontains"),
           sort_fields=("first_name", "last_name")),     # sort multi-field
    Column("status", "Status", attr="is_active", filter="select",
           choices=(("1", "Aktif"), ("0", "Nonaktif")),
           coerce=lambda v: v == "1", lookups=("is_active",),
           badges={True: ("success", "Aktif"), False: ("error", "Nonaktif")},
           sort_fields=("is_active",)),
    Column("role", "Role", attr="is_superuser", filter="select",
           choices=(("1", "Superuser"), ("0", "User")),
           coerce=lambda v: v == "1", lookups=("is_superuser",),
           badges={True: ("warning", "Superuser"), False: ("ghost", "User")}),
           # role tidak diberi sort_fields -> header tetap teks biasa

    # Kolom aksi, cukup satu Column dengan actions=
    Column("aksi", "Aksi", actions=(
        Action("Edit", "bi-pencil", "iam:user_edit",
               perm="auth.change_user"),
        Action("Hapus", "bi-trash", "iam:user_delete", style="btn-error",
               confirm=True, name_attr="username",
               perm="auth.delete_user",
               show_if=lambda u: not u.is_superuser),   # superuser tidak bisa dihapus dari sini
    )),

    # 
    Column("aksi", "Aksi", actions=(
        Action("Edit", "bi-pencil", "iam:user_edit", perm="auth.change_user"),
        Action("Hapus", "bi-trash", "iam:user_delete", style="btn-error",
            hx_method="post",
            hx_confirm='Hapus user "{name}"? Tindakan ini tidak bisa dibatalkan.',
            name_attr="username",
            perm="auth.delete_user",
            show_if=lambda u: not u.is_superuser),
    )),
# 
    Column("aksi", "Aksi", actions=(
        Action("Edit", "bi-pencil", "iam:user_edit", perm="auth.change_user"),
        Action("Ubah akses", "bi-shield-lock", "iam:user_set_role",
            style="btn-warning", modal=True, perm="auth.change_user"),
        Action("Hapus", "bi-trash", "iam:user_delete", style="btn-error",
            hx_method="post",
            hx_confirm='Hapus user "{name}"?',
            name_attr="username", perm="auth.delete_user",
            show_if=lambda u: not u.is_superuser),
    )),
]


@login_required
def user_list(request):
    return render_table(
        request,
        qs=User.objects.all(),
        columns=USER_COLUMNS,
        list_url="iam:user_list",
        page_template="iam/users/list.html",
        row_actions_template="iam/users/_actions.html",
        default_sort=("username",),       # dipakai kalau tidak ada ?sort=
    )

# if search dynamic
# def get_product_columns():
#     return [
#         Column("name", "Nama", filter="text", lookups=("name__icontains",)),
#         Column("kategori", "Kategori", attr="category.name", filter="select",
#                lookups=("category_id",),
#                choices=tuple((str(c.pk), c.name) for c in Category.objects.all())),
#     ]


# @login_required
# def product_list(request):
#     return render_table(
#         request,
#         qs=Product.objects.select_related("category").order_by("name"),
#         columns=get_product_columns(),
#         list_url="products:list",
#         page_template="products/list.html",
#         row_actions_template="products/_actions.html",
#     )

# from django.contrib import messages
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from django.views.decorators.http import require_POST

# @login_required
# @require_POST
# def user_delete(request, pk):
#     obj = get_object_or_404(User, pk=pk)
#     name = obj.username
#     obj.delete()
#     messages.success(request, f'User "{name}" berhasil dihapus.')

#     if request.headers.get("HX-Request"):
#         return HttpResponse(headers={"HX-Refresh": "true"})
#     return redirect("iam:user_list")

# iam/views.py
# from core.tables import modal_form
# from .forms import UserRoleForm

# @login_required
# def user_set_role(request, pk):
#     obj = get_object_or_404(User, pk=pk)
#     return modal_form(
#         request,
#         form_class=UserRoleForm,
#         instance=obj,
#         title=f"Ubah akses: {obj.username}",
#         success_message=f'Akses "{obj.username}" diperbarui.',
#     )