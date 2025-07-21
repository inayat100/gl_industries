# -*- coding: utf-8 -*-
{
    "name": """IR Sale Report """,
    "version": "18.0",
    "icon": "",
    "category": "",
    "author": "Inayat Rasool",
    "depends": [
        "base", "sale", "mail", "purchase", "account", "mrp"
    ],
    "description": """
    """,
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/cron.xml',
        'configuration/account_move_configration.xml',
        'configuration/access_right_report_configration_view.xml',
        'configuration/product_template_configration.xml',
        'configuration/purchase_order_configration.xml',
        'configuration/sale_order_configration.xml',
        'configuration/sale_order_report_configration.xml',
        'views/main_menu.xml',
        'views/account_move.xml',
        'views/product_view.xml',
        'views/production_planing_view.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/sale_order_fabric_view.xml',
        'views/sale_order_report_view.xml',
        'views/sample_planing_view.xml',
        'views/production_view.xml',
        'views/production_move_report_view.xml',
    ],
    "demo": [
    ],
    "installable": True,
    "license": "LGPL-3",
}
