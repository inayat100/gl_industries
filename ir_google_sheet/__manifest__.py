# -*- coding: utf-8 -*-
{
    "name": """IR Google Sheet Config""",
    "version": "18.0",
    "icon": "",
    "category": "",
    "author": "Inayat Rasool",
    "description": """
   """,
    "depends": [
        "base", "mail"
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/api_report_configuration_view.xml',
        'views/google_sheet_configuration_view.xml',
        'views/google_sheet_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
