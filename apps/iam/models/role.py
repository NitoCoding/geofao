from django.contrib.auth.models import Permission
from django.db import models
from django.core.exceptions import ValidationError

from config import settings


class Role(models.Model):
    """
    Pengganti/Extension Group.
    Beda: bisa punya hierarki (parent-child) dan scope.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)  # 'admin', 'dosen', 'mahasiswa'
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Django built-in permissions (optional, bisa gunakan ini saja)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_roles'
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        """Aggregate permissions dari parent hierarchy"""
        perms = set(self.permissions.all())
        if self.parent:
            perms.update(self.parent.get_all_permissions())
        return perms


class UserRole(models.Model):
    """
    Mapping many-to-many antara User dan Role dengan Unit Scope.

    Contoh penggunaan:
    - User A sebagai "Kepala Prodi" di Unit Manajemen
    - User A sebagai "Dosen" di Unit Akuntansi
    - User B sebagai "Kepala Biro" di Unit Keuangan (global scope)

    Field unit_kerja bisa null untuk role global (is_unit_scoped=False).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )


    # Metadata assignment
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned'
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    # Periode jabatan (opsional)
    periode_mulai = models.DateField(null=True, blank=True, verbose_name='Periode Mulai')
    periode_selesai = models.DateField(null=True, blank=True, verbose_name='Periode Selesai')

    class Meta:
        ordering = ['-assigned_at']
        constraints = [
            # Unique together: user + role + unit (unit bisa null)
            models.UniqueConstraint(
                fields=['user', 'role', ],
                name='unique_user_role'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def clean(self):
        """Validasi business rules"""
        # Validasi: Periode selesai harus setelah periode mulai
        if self.periode_mulai and self.periode_selesai:
            if self.periode_selesai > self.periode_mulai:
                raise ValidationError("Periode selesai harus setelah periode mulai.")

    # ============ PROPERTIES ============

    @property
    def is_periode_active(self):
        """Cek apakah jabatan masih dalam periode aktif"""
        from datetime import date
        today = date.today()

        if self.periode_mulai and today < self.periode_mulai:
            return False
        if self.periode_selesai and today > self.periode_selesai:
            return False
        return True

    @property
    def is_effective(self):
        """Role efektif jika aktif dan dalam periode"""
        return self.is_active and self.is_periode_active

    @property
    def scope_display(self):
        """Display scope untuk UI"""
        # if self.unit_kerja:
        #     return f"{self.unit_kerja.nama} ({self.unit_kerja.tipe})"
        return "Global (Semua Unit)"

    # ============ METHODS ============

    # def has_access_to_unit(self, unit):
    #     """
    #     Cek apakah role ini memberikan akses ke unit tertentu.

    #     Logic:
    #     - Jika unit_kerja null (global): akses ke semua unit
    #     - Jika unit_kerja == unit: akses langsung
    #     - Jika unit_kerja adalah parent dari unit: akses hierarki
    #     """
    #     if not self.is_effective:
    #         return False

    #     # Global scope
    #     if not self.unit_kerja:
    #         return True

    #     # Direct match
    #     if self.unit_kerja == unit:
    #         return True

    #     # Hierarchy check: cek apakah unit adalah descendant dari unit_kerja
    #     current = unit
    #     while current.parent:
    #         if current.parent == self.unit_kerja:
    #             return True
    #         current = current.parent

    #     return False

    # def get_accessible_units(self):
    #     """
    #     Get queryset semua unit yang bisa diakses oleh role ini.
    #     """
    #     from apps.master_data.models import UnitKerja

    #     if not self.is_effective:
    #         return UnitKerja.objects.none()

    #     # Global scope: semua unit
    #     if not self.unit_kerja:
    #         return UnitKerja.objects.filter(is_active=True)

    #     # Unit scope: unit itu sendiri + semua descendants
    #     accessible_ids = [self.unit_kerja.id]

    #     def collect_children(unit):
    #         for child in unit.children.filter(is_active=True):
    #             accessible_ids.append(child.id)
    #             collect_children(child)

    #     collect_children(self.unit_kerja)
    #     return UnitKerja.objects.filter(id__in=accessible_ids)
