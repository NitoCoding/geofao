"""
Menu Service - Role-Based Menu Builder

Menyusun menu tree berdasarkan role user.
Fokus pada role-based access, bukan Django permissions.
"""

from apps.iam.models import MenuRole, Menu, Role
from apps.core.decorators import get_user_roles
from django.urls import reverse, NoReverseMatch


class MenuService:
    """
    Service untuk membangun menu tree berdasarkan role user.
    
    Strategi:
    1. Ambil semua role yang dimiliki user
    2. Cek MenuRole (explicit menu assignment) untuk setiap role
    3. Jika ada explicit assignment, gunakan itu
    4. Jika tidak ada, gunakan fallback (menu tanpa role restriction)
    5. Bangun tree structure dengan parent-child relationship
    """
    
    @staticmethod
    def get_user_menu(user):
        """
        Build menu tree untuk user berdasarkan role-nya.
        
        Args:
            user: User instance
            
        Returns:
            list: Tree structure of menus
        """
        if not user.is_authenticated:
            return []
        
        # Superuser dapat semua menu
        if user.is_superuser:
            return MenuService._get_all_menus()
        
        # 1. Ambil semua role codes user
        user_role_codes = get_user_roles(user)
        
        # DEBUG: Log untuk troubleshooting
        # print(f"DEBUG - User: {user.username}, Roles: {user_role_codes}, IsSuperuser: {user.is_superuser}")
        
        if not user_role_codes:
            return []
        
        # 2. Ambil semua menu aktif (single query)
        all_active_menus = Menu.objects.filter(
            is_active=True
        ).prefetch_related('menu_roles', 'menu_roles__role')
        
        # 3. Ambil menu IDs yang explicitly di-assign ke role user
        explicit_menu_ids = MenuService._get_explicit_menu_ids(user_role_codes)
        
        # DEBUG: Log explicit menu IDs
        # print(f"DEBUG - Explicit menu IDs for roles {user_role_codes}: {explicit_menu_ids}")
        
        # 4. Determine accessible menu IDs (WHITELIST approach)
        accessible_ids = MenuService._get_accessible_menu_ids(
            all_active_menus, 
            user_role_codes, 
            explicit_menu_ids
        )
        
        # DEBUG: Log accessible IDs
        # print(f"DEBUG - Accessible menu IDs: {accessible_ids}")
        
        if not accessible_ids:
            return []
        
        # 5. Include parent menus untuk menjaga struktur tree
        final_ids = MenuService._include_parents(all_active_menus, accessible_ids)
        
        # 6. Build tree structure
        return MenuService._build_tree(all_active_menus, final_ids)
    
    @staticmethod
    def _get_all_menus():
        """Ambil semua menu untuk superuser."""
        all_menus = Menu.objects.filter(is_active=True).prefetch_related(
            'menu_roles', 'menu_roles__role'
        )
        all_ids = set(all_menus.values_list('id', flat=True))
        return MenuService._build_tree(all_menus, all_ids)
    
    @staticmethod
    def _get_explicit_menu_ids(user_role_codes):
        """
        Ambil menu IDs yang explicitly di-assign ke role user.
        
        Args:
            user_role_codes: set of role codes
            
        Returns:
            set: Menu IDs yang di-assign
        """
        if not user_role_codes:
            return set()
        
        return set(
            MenuRole.objects.filter(
                role__code__in=user_role_codes,
                role__is_active=True
            ).values_list('menu_id', flat=True)
        )
    
    @staticmethod
    def _get_accessible_menu_ids(all_menus, user_role_codes, explicit_menu_ids):
        """
        Determine which menus are accessible untuk user.
        
        Strategi WHITELIST:
        - Jika ada explicit MenuRole: hanya menu yang explicitly di-assign
        - Jika tidak ada explicit MenuRole: tidak ada menu yang di-assign
          (user tidak melihat menu apapun kecuali superuser)
        
        Args:
            all_menus: QuerySet of Menu objects
            user_role_codes: set of user's role codes
            explicit_menu_ids: set of menu IDs explicitly assigned to user's roles
            
        Returns:
            set: Accessible menu IDs
        """
        accessible_ids = set()
        
        # WHITELIST APPROACH:
        # Hanya tampilkan menu yang explicitly di-assign ke role user
        # Jika tidak ada explicit assignment, user tidak melihat menu apapun
        
        for menu in all_menus:
            if menu.id in explicit_menu_ids:
                accessible_ids.add(menu.id)
        
        return accessible_ids
    
    @staticmethod
    def _include_parents(all_menus, accessible_ids):
        """
        Include semua parent menu IDs untuk menjaga struktur tree.
        
        Args:
            all_menus: QuerySet of all menus
            accessible_ids: set of accessible menu IDs
            
        Returns:
            set: Final menu IDs including parents
        """
        final_ids = set(accessible_ids)
        menu_map = {m.id: m for m in all_menus}
        
        for m_id in list(accessible_ids):
            curr = menu_map.get(m_id)
            while curr and curr.parent_id:
                final_ids.add(curr.parent_id)
                curr = menu_map.get(curr.parent_id)
        
        return final_ids
    
    @staticmethod
    def _build_tree(all_menus, menu_ids):
        """
        Build tree structure dari flat menu list.
        
        Args:
            all_menus: QuerySet of menus
            menu_ids: set of menu IDs to include
            
        Returns:
            list: Tree structure sorted by order
        """
        # Filter menus
        relevant_menus = [m for m in all_menus if m.id in menu_ids]
        
        # Build node map
        menu_map = {}
        for m in relevant_menus:
            menu_map[m.id] = {
                'id': m.id,
                'name': m.name,
                'code': m.code,
                'icon': m.icon,
                'url': resolve_url(m.path),
                'type': m.menu_type,
                'order': m.order,
                'children': []
            }
        
        # Build tree
        root_items = []
        for m in relevant_menus:
            node = menu_map[m.id]
            if m.parent_id and m.parent_id in menu_map:
                menu_map[m.parent_id]['children'].append(node)
            else:
                root_items.append(node)
        
        # Sort children dan root items
        for node in menu_map.values():
            node['children'].sort(key=lambda x: x['order'])
        
        root_items.sort(key=lambda x: x['order'])
        return root_items
    
    @staticmethod
    def user_can_access_menu(user, menu_code):
        """
        Cek apakah user bisa akses menu tertentu.
        
        Args:
            user: User instance
            menu_code: string code dari menu
            
        Returns:
            bool
        """
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        try:
            menu = Menu.objects.get(code=menu_code, is_active=True)
        except Menu.DoesNotExist:
            return False
        
        user_role_codes = get_user_roles(user)
        
        # Cek explicit MenuRole
        has_menu_role = MenuRole.objects.filter(
            menu=menu,
            role__code__in=user_role_codes,
            role__is_active=True
        ).exists()
        
        if has_menu_role:
            return True
        
        # Cek role di menu itu sendiri
        menu_role_codes = set(
            menu.menu_roles.filter(role__is_active=True)
            .values_list('role__code', flat=True)
        )
        
        if not menu_role_codes:
            # Menu tidak punya role restriction
            return True
        
        return bool(user_role_codes & menu_role_codes)
    
    @staticmethod
    def get_menu_for_role(role_code):
        """
        Get menu tree untuk role tertentu.
        
        Args:
            role_code: string role code
            
        Returns:
            list: Menu tree untuk role tersebut
        """
        try:
            role = Role.objects.get(code=role_code, is_active=True)
        except Role.DoesNotExist:
            return []
        
        # Get explicit menu assignments
        explicit_menu_ids = set(
            MenuRole.objects.filter(role=role).values_list('menu_id', flat=True)
        )
        
        if explicit_menu_ids:
            all_menus = Menu.objects.filter(is_active=True).prefetch_related('menu_roles')
            final_ids = MenuService._include_parents(all_menus, explicit_menu_ids)
            return MenuService._build_tree(all_menus, final_ids)
        
        # Fallback: menu yang tidak punya role restriction
        all_menus = Menu.objects.filter(is_active=True).prefetch_related('menu_roles')
        accessible_ids = set()
        
        for menu in all_menus:
            menu_role_codes = set(
                mr.role.code for mr in menu.menu_roles.all() if mr.role.is_active
            )
            if not menu_role_codes:
                accessible_ids.add(menu.id)
        
        if accessible_ids:
            final_ids = MenuService._include_parents(all_menus, accessible_ids)
            return MenuService._build_tree(all_menus, final_ids)
        
        return []


def resolve_url(path):
    """
    Resolve URL path - bisa URL name atau hardcoded path.
    
    Args:
        path: string URL name (e.g., 'accounts:user_list') atau path (e.g., '/about/')
        
    Returns:
        string: Resolved URL atau '#' jika tidak valid
    """
    if not path or path == '#':
        return '#'
    
    try:
        return reverse(path)
    except NoReverseMatch:
        return path