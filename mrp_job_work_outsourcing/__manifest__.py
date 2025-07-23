# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Job Work Outsourcing',
    'version': '18.0.1.0.0',
    'summary': 'Manage outsourced manufacturing processes like cutting, stitching, etc.',
    'description': """
This module enhances Odoo Manufacturing to handle outsourced job work.
Key Features:
- Define custom manufacturing processes (Cutting, Printing, etc.).
- Create sequential process routes for job work.
- Add a 'Job Work' tab to Manufacturing Orders to track outsourced processes.
- Issue materials to and receive finished goods from multiple vendors for each process.
- Enforce validations to ensure quantity constraints and sequential processing.
- Track vendor performance and process status.
    """,
    'author': 'Rahul Kumar',
    'category': 'Manufacturing/Manufacturing',
    'depends': ['mrp', 'ir_sale_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/job_work_process_views.xml',
        'views/job_work_route_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_jobwork_line_views.xml',
        'views/job_work_analysis_views.xml',
        'wizard/job_work_wizard_views.xml',
        'views/job_work_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
