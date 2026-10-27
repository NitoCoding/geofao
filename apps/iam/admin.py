from django.contrib import admin

from apps.iam.models import User,Menu, MenuRole, Role, UserRole
from django.contrib.auth.models import Permission

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


class MenuChildInline(admin.TabularInline):
    model = Menu
    fk_name = 'parent'
    fields = ('name', 'code', 'menu_type', 'path', 'order', 'is_active')
    extra = 0
    show_change_link = True
    verbose_name = "Sub Menu"
    verbose_name_plural = "Daftar Sub Menu"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'menu_type', 'parent', 'order', 'is_active')
    list_filter = ('menu_type', 'is_active')
    search_fields = ('name', 'code', 'path')
    ordering = ('parent__id', 'order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'icon', 'path', 'menu_type', 'parent', 'order', 'is_active')
        }),
        ('Permissions', {
            'fields': ('required_permissions',),
            'classes': ('collapse',),
        }),
    )
    inlines = [MenuChildInline]

@admin.register(MenuRole)
class MenuRoleAdmin(admin.ModelAdmin):
    list_display = ('menu', 'role')
    search_fields = ('menu__name', 'role__name')
    ordering = ('menu__name', 'role__name')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role__name')
    ordering = ('user__username', 'role__name')

# Import Permission model first
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ('name', 'codename')
    ordering = ('content_type', 'name')
