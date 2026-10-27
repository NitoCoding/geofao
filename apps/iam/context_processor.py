import logging
from .service.menu_builder import MenuService


logger = logging.getLogger(__name__)


def menu_context(request):
    if request.user.is_authenticated:
        menu_items = MenuService.get_user_menu(request.user)
        # ic(menu_items)  # Debug: Lihat menu yang dihasilkan untuk user ini
        logger.info(menu_items)
    else:
        menu_items = [
            {'type': 'header', 'name': 'General', 'children': [
                {'name': 'Peta Interaktif', 'url': '/spatial/map/', 'icon': 'bi bi-map'},
            ]},
        ]
    
    #
    # menu_items = [
    #     {
    #         "name": "MENU UTAMA",
    #         "url": "",
    #         "type": "header",
    #         "icon": "",
    #         "children": [
    #             {
    #                 "name": "Dashboard",
    #                 "url": "",
    #                 "type": "item",
    #                 "icon": "ri-dashboard-line",
    #             },
    #             {
    #                 "name": "Anggaran",
    #                 "url": "",
    #                 "type": "item",
    #                 "icon": "ri-wallet-line",
    #             },
    #             {
    #                 "name": "Transaksi",
    #                 "url": "",
    #                 "type": "item",
    #                 "icon": "ri-arrow-left-right-line",
    #             },
    #             {
    #                 "name": "Laporan",
    #                 "url": "",
    #                 "type": "item",
    #                 "icon": "ri-line-chart-line",
    #             },
    #             {
    #                 "name": "Departemen",
    #                 "url": "master-data/unit-kerja/",
    #                 "type": "item",
    #                 "icon": "ri-building-line",
    #             },
    #         ],
    #     }
    # ]

    return {
        "menu_items": menu_items,
    }
