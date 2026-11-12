# Plan: Simplifikasi `core/tables.py`

## 1. Masalah Saat Ini

File [`core/tables.py`](file:///d:\Proyek\Penelitian\geoai\apps\core\tables.py) saat ini bermasalah:

| Masalah | Detail |
|---|---|
| **Overengineered** | 3 dataclass (`Action`, `Column`), 4 fungsi, 2 concern (tabel + form) dalam 1 file |
| **Dead code** | Tidak ada satu pun file Python yang import `tables.py` |
| **Action dataclass terlalu kompleks** | 11 field, mencoba handle semua skenario tombol |
| **Column dataclass terlalu banyak field** | 13 field, banyak tidak terpakai (`cell`, `actions`, `path`) |
| **Campur aduk** | `render_table` + `style_form` + `modal_form` dalam satu file |
| **Template terkait tidak dipakai** | `filter_table.html`, `_table_rows.html`, `_modal_form.html` — semua dead |

## 2. Target: `tables.py` Versi Baru

Prinsip: **hanya handle apa yang benar-benar umum**, sisanya serahkan ke template.

### 2.1 `TableCol` — Dataclass minimal

```python
@dataclass
class TableCol:
    key: str          # field name ORM
    label: str        # tampilan di header
    filter: str = ""  # "text" | "select" | "" (kosong = tidak bisa difilter)
    choices: list = field(default_factory=list)  # untuk select filter
```

**Dihapus:** `attr`, `lookups`, `coerce`, `badges`, `cell`, `width`, `sort_fields`, `actions`, `path`, `build_q()`

### 2.2 `render_table` — Fungsi ringan

```python
def render_table(request, qs, cols, template, per_page=20):
```

Hanya handle:
- Filter otomatis untuk field langsung (`key__icontains`)
- Sorting via `?sort=field` atau `?sort=-field`
- Pagination
- Pass `cols` + `rows` ke template

**Tidak handle:**
- Filter relasi (tetap manual di view)
- Action buttons (tetap di template)
- Custom cell rendering (badge, status — di template manual)
- Form styling
- Modal form

### 2.3 Yang dipisah ke file terpisah

| Fungsi | Pindah ke |
|---|---|
| `style_form` | `core/forms.py` atau inline di view |
| `modal_form` | `core/forms.py` atau inline di view |

### 2.4 `Action` — Hapus total

Aksi tombol tetap di template HTML. Tidak perlu dataclass Python.

## 3. Component Templates

### 3.1 `components/_pagination.html` (BARU)

Partial untuk pagination yang identik di semua tabel. Terima parameter:
- `page_obj` — Paginator page object
- `filter_qs` — query string untuk preserve filter

### 3.2 `components/_table_actions.html` (BARU - opsional)

Partial untuk tombol edit/delete standar. Terima parameter:
- `obj` — object instance
- `edit_url` — url name (optional)
- `delete_url` — url name (optional)
- `confirm_msg` — pesan konfirmasi (optional)

### 3.3 Template lama — Hapus

- `components/filter_table.html` — dead code
- `components/_table_rows.html` — dead code
- `components/_modal_form.html` — dead code

### 3.4 Template yang dipertahankan

- `components/form_modal.html` — masih dipakai (cek dulu)
- `components/_table_footer.html` — masih dipakai (cek dulu)

## 4. Cara Pakai di View

### Contoh: User List (FBV)

```python
def user_list(request):
    qs = User.objects.all().prefetch_related("assignment_roles__role")

    # Filter relasi — manual, tidak otomatis
    filter_role = request.GET.get("filter_role", "")
    if filter_role:
        qs = qs.filter(roles__code=filter_role).distinct()

    cols = [
        TableCol("username", "Username", filter="text"),
        TableCol("email", "Email", filter="text"),
        TableCol("filter_role", "Role", filter="select",
                 choices=[("admin", "Admin"), ("tenaga_ahli", "Tenaga Ahli")]),
    ]

    return render_table(request, qs, cols, template="users/list.html")
```

### Template `users/list.html`

```django
{% extends "base.html" %}
{% block content %}
<table>
  <thead>
    <tr>
      {% for col in cols %}
        <th>{{ col.label }}</th>
      {% endfor %}
      <th>Aksi</th>
    </tr>
    <tr>{% include "components/_table_filters.html" %}</tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr>
      {% for col in cols %}
        <td>{{ row.obj|attr:col.key }}</td>
      {% endfor %}
      <td>
        {% include "components/_table_actions.html" with
          obj=row.obj
          edit_url="iam:user_edit"
          delete_url="iam:user_delete"
        %}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% include "components/_pagination.html" %}
{% endblock %}
```

## 5. Reference Pattern: CBV Style (UserListView)

Pattern dari [`UserListView`](file:///d:\Proyek\Penelitian\geoai\apps\iam\views\user.py#L14-93) ini yang akan dipakai sebagai standar untuk SIAKAD.

### 5.1 Struktur View

```python
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "iam/users/index.html"
    context_object_name = "users"
    paginate_by = 10

    def get_template_names(self):
        """HTMX: partial table, non-HTMX: full page"""
        if self.request.headers.get("HX-Request") or self.request.htmx:
            return "iam/users/datatable.html"
        return self.template_name
```

### 5.2 Filter — Eksplisit di `get_queryset()`

```python
    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        # Global search
        search = request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
            )

        # Per-column filters — eksplisit, satu per satu
        filter_username = request.GET.get("filter_username", "").strip()
        if filter_username:
            qs = qs.filter(username__icontains=filter_username)

        # Filter relasi — manual, tidak pakai magic lookup
        filter_role = request.GET.get("filter_role", "").strip()
        if filter_role:
            qs = qs.filter(roles__code=filter_role).distinct()

        # N+1: prefetch_related untuk relasi yang di-loop di template
        qs = qs.prefetch_related("assignment_roles__role")

        return qs.order_by("-date_joined")
```

### 5.3 Context — Eksplisit di `get_context_data()`

```python
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # Summary stats
        context["total_users"] = User.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()

        # Filter values — untuk persistensi input di template
        context["filter_username"] = request.GET.get("filter_username", "")
        context["filter_role"] = request.GET.get("filter_role", "")

        # Dynamic choices untuk dropdown filter
        context["available_roles"] = Role.objects.filter(is_active=True)

        # Query string untuk pagination (exclude page)
        params = request.GET.copy()
        params.pop("page", None)
        context["filter_qs"] = urlencode(params)

        return context
```

### 5.4 Ringkasan Pola

| Komponen | Pattern |
|---|---|
| View class | `LoginRequiredMixin` + `ListView` |
| Template switching | `get_template_names()` cek `HX-Request` |
| Filter | Eksplisit di `get_queryset()`, satu var per field |
| Filter relasi | Manual `filter(rel__field=value)` |
| N+1 | `prefetch_related()` / `select_related()` di queryset |
| Summary stats | Hitung di `get_context_data()` |
| Filter persistensi | Simpan `request.GET` value ke context |
| Pagination | Bawaan `ListView.paginate_by` |
| Filter query string | `urlencode(params)` exclude `page` |

### 5.5 Kapan pakai CBV vs FBV + `render_table`

| Situasi | Pakai |
|---|---|
| View sederhana, filter dikit, aksi standar | **CBV** (UserListView pattern) |
| View dengan filter/sort/ pagination standar | **CBV** (UserListView pattern) |
| View dengan banyak filter custom | **CBV** (UserListView pattern) |
| Mau cepat buat tabel baru tanpa nulis boilerplate | **FBV + `render_table`** |
| Butuh kontrol penuh, logic non-standar | **CBV** (UserListView pattern) |

> **Catatan:** `render_table` hanya untuk kasus di mana kita mau mengurangi boilerplate filter/sort/pagination yang benar-benar identik. Untuk SIAKAD, sebagian besar view tetap pakai CBV pattern di atas karena lebih eksplisit dan mudah di-maintain.

## 7. Catatan untuk SIAKAD (Proyek Besar)

| Situasi | Pendekatan |
|---|---|
| Filter field langsung (username, email) | Otomatis via `render_table` |
| Filter relasi (roles__code) | Manual di view |
| Aksi tombol standar (edit/delete) | Partial `_table_actions.html` |
| Aksi tombol khusus | Tulis langsung di template |
| N+1 problem | `prefetch_related` / `select_related` di view |
| Cell custom (badge, status) | Tulis langsung di template |
| Pagination | Partial `_pagination.html` |

### 7.1 Keuntungan untuk SIAKAD

1. **Konsistensi UI** — semua tabel pakai render_table + partial yang sama
2. **DRY untuk boilerplate** — filter, sort, pagination tidak perlu ditulis ulang
3. **Fleksibel** — cell custom, aksi, filter relasi tetap eksplisit di template/view
4. **Mudah di-debug** — tidak ada magic abstraction, filter manual jelas
5. **Zero dependency** — tidak perlu django-filters atau library lain

## 8. Langkah Eksekusi

1. Tulis ulang `core/tables.py` (hapus Action, sederhanakan Column, hapus form functions)
2. Buat `core/forms.py` untuk `style_form` + `modal_form` (jika masih diperlukan)
3. Buat `components/_pagination.html`
4. Buat `components/_table_actions.html` (opsional)
5. Hapus template dead: `filter_table.html`, `_table_rows.html`, `_modal_form.html`
6. Verifikasi tidak ada import yang broken
