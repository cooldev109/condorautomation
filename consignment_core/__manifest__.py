# -*- coding: utf-8 -*-
{
    'name': 'Consignment Core',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Core consignment management system',
    'description': """
        Consignment Core Module
        =======================
        - Manage consignment items from customers
        - Auto-create products for consignment items
        - Track item lifecycle (received → listed → sold → paid)
        - Integrate with stock locations
        - Commission and pricing management
        - Multi-image support for items
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'stock',
        'sale_management',
        'portal',
    ],
    'data': [
        # Security
        'security/consignment_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/sequence_data.xml',

        # Views
        'views/res_partner_views.xml',
        'views/consignment_item_views.xml',
        'views/consignment_menus.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'consignment_core/static/src/css/custom_logo.css',
        ],
        'web.assets_backend': [
            'consignment_core/static/src/css/custom_logo.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
