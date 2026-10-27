from django.db import models
from .role import Role
from django.contrib.auth.models import Permission

class Menu(models.Model):
    """
    Menu tree structure.
    Frontend akan render ini berdasarkan role user.
    """
    MENU_TYPES = (
        ('header', 'Header Section'), # Teks pembantu (misal: "MASTER DATA")
        ('parent', 'Parent Menu'),    # Menu yang punya dropdown
        ('item', 'Single Item'),      # Menu klik langsung
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, blank=True, help_text="Kode unik untuk referensi (misal: 'subjects', 'schedule')")
    icon = models.CharField(max_length=50, blank=True)
    path = models.CharField(max_length=200, blank=True, help_text="/admin/subjects atau /jadwal")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
    menu_type = models.CharField(max_length=10, choices=MENU_TYPES, default='item')
    order = models.PositiveSmallIntegerField(default=0)
    required_permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['parent__id', 'order', 'name']

    def __str__(self):
        return self.name

    def get_children_recursive(self):
        """Get all descendants"""
        children = []
        for child in self.children.filter(is_active=True):
            children.append(child)
            children.extend(child.get_children_recursive())
        return children

class MenuRole(models.Model):
    """
    Mapping many-to-many antara Menu dan Role.
    """
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='menu_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='menu_roles'
    )

    def __str__(self):
        return f"{self.menu.name} - {self.role.name}"

    class Meta:
        unique_together = ('menu', 'role')
