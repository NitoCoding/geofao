from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Extend User model untuk kebutuhan custom.
    Bisa ditambah field seperti 'is_dosen', 'is_mahasiswa', dll
    """
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    roles = models.ManyToManyField(
        'Role',
        through_fields=('user', 'role'),
        through='UserRole',
        related_name='users'  # Ini agar dari Role bisa panggil role.users.all()
    )

    # ============ ROLE & UNIT HELPERS ============

    def get_effective_roles(self):
        """Get semua UserRole yang aktif dan dalam periode"""
        return self.assignment_roles.filter(is_active=True)

    def get_roles_for_unit(self, unit):
        """Get roles yang dimiliki user untuk unit tertentu"""
        effective = self.get_effective_roles()
        return [
            ur for ur in effective
            if ur.has_access_to_unit(unit)
        ]

    def get_accessible_units(self):
        """
        Get queryset semua unit yang bisa diakses oleh user.
        Gabungan dari semua roles.
        """
        from apps.master_data.models import UnitKerja

        accessible_ids = set()

        for user_role in self.get_effective_roles():
            units = user_role.get_accessible_units()
            accessible_ids.update(units.values_list('id', flat=True))

        return UnitKerja.objects.filter(id__in=accessible_ids)

    def has_access_to_unit(self, unit):
        """Cek apakah user punya akses ke unit tertentu"""
        for user_role in self.get_effective_roles():
            if user_role.has_access_to_unit(unit):
                return True
        return False


    def get_primary_unit(self):
        """
        Get unit utama user (unit dari role pertama yang scoped).
        Return None jika hanya punya role global.
        """
        for user_role in self.get_effective_roles():
            if user_role.unit_kerja:
                return user_role.unit_kerja
        return None

    # ============ PERMISSION HELPERS ============

    def get_all_permissions(self):
        """Override untuk include permissions dari roles"""
        perms = super().get_all_permissions()

        for user_role in self.get_effective_roles():
            role_perms = user_role.role.get_all_permissions()
            perms.update({f"{p.content_type.app_label}.{p.codename}" for p in role_perms})

        return perms

    def has_role(self, role_code):
        """Cek apakah user punya role tertentu (di unit manapun)"""
        return self.get_effective_roles().filter(role__code=role_code).exists()

    def has_role_in_unit(self, role_code, unit):
        """Cek apakah user punya role tertentu di unit tertentu"""
        return self.get_roles_for_unit(unit) and any(
            ur.role.code == role_code for ur in self.get_roles_for_unit(unit)
        )
