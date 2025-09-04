# -*- coding: utf-8 -*-
{
    "name": """IR Report""",
    "version": "18.0",
    "icon": "",
    "category": "Sales",
    "author": "Inayat Rasool",
    "description": """
   """,
    "depends": [
        "base", "sale", "mail", "purchase", "account", "product", "ir_sale_report", "ir_record_lock_config"
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'data/document_type_master.xml',
        'views/quality_report_view.xml',
        'views/quality_report_conf_view.xml',
        'views/measurement_view.xml',
        'views/measurement_conf_view.xml',
        'views/measurement_line_view.xml',
        'views/pps_report_view.xml',
        'views/pps_report_conf_view.xml',
        'views/pps_report_line_view.xml',
        'views/res_user_view.xml',
        'views/api_report_configration.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
