# -*- coding: utf-8 -*-
{
    "name": """IR BOM Config""",
    "version": "18.0",
    "icon": "",
    "category": "",
    "author": "Inayat Rasool",
    "description": """
   """,
    "depends": [
        "base", "ir_sale_report", "ir_record_lock_config", "mrp", "mail"
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/bom_route_view.xml',
        'views/product_template.xml',
        'views/bom_view.xml',
        'views/user_view.xml',
        'views/api_report_configration.xml',
        'views/bom_line_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
