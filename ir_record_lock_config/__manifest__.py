# -*- coding: utf-8 -*-
{
    "name": """IR Record Config""",
    "version": "18.0",
    "icon": "",
    "category": "",
    "author": "Inayat Rasool",
    "description": """
   """,
    "depends": [
        "base", "sale", "mail", "purchase", "account", "product"
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/record_lock_config_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
