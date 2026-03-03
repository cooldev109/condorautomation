# -*- coding: utf-8 -*-
{
    'name': 'Consignment Intake',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Quick intake wizard for consignment items',
    'description': """
        Consignment Intake Module
        ==========================
        Provides a streamlined wizard for quickly intaking multiple consignment items:
        * Batch item creation
        * Quick entry form with editable tree view
        * Photo upload during intake
        * Automatic transition to 'received' state
        * Pre-filled default values for faster data entry
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['consignment_core'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/consignment_intake_wizard_views.xml',
        'views/consignment_intake_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
