from django.urls import path
from apps.iam.views.authentication import login_view, logout_view
from apps.iam.views.user import UserListView, UserCreateView, UserUpdateView, UserDeleteView
from apps.iam.views.menu import MenuListView, MenuCreateView, MenuUpdateView, MenuDeleteView
from apps.iam.views.menu_role import MenuRoleListView, MenuRoleCreateView, MenuRoleUpdateView, MenuRoleDeleteView
from apps.iam.views.role_permission import RolePermissionListView, RolePermissionCreateView, RolePermissionDeleteView
from apps.iam.views.profile import profile_view

app_name = 'iam'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Profile
    path('profile/', profile_view, name='profile'),

    # User Management
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Menu Management
    path('menus/', MenuListView.as_view(), name='menu_list'),
    path('menus/create/', MenuCreateView.as_view(), name='menu_create'),
    path('menus/<int:pk>/edit/', MenuUpdateView.as_view(), name='menu_edit'),
    path('menus/<int:pk>/delete/', MenuDeleteView.as_view(), name='menu_delete'),

    # Menu-Role Management
    path('menu-roles/', MenuRoleListView.as_view(), name='menu_role_list'),
    path('menu-roles/create/', MenuRoleCreateView.as_view(), name='menu_role_create'),
    path('menu-roles/<int:pk>/edit/', MenuRoleUpdateView.as_view(), name='menu_role_edit'),
    path('menu-roles/<int:pk>/delete/', MenuRoleDeleteView.as_view(), name='menu_role_delete'),

    # Role-Permission Management
    path('role-permissions/', RolePermissionListView.as_view(), name='role_permission_list'),
    path('role-permissions/create/', RolePermissionCreateView.as_view(), name='role_permission_create'),
    path('role-permissions/<int:pk>/delete/', RolePermissionDeleteView.as_view(), name='role_permission_delete'),
]
