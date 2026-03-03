# -*- coding: utf-8 -*-
{
    'name': 'Consignment eBay Integration',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Integrate consignment items with eBay marketplace',
    'description': """
        Consignment eBay Integration
        =============================

        Features:
        ---------
        * eBay OAuth 2.0 authentication
        * Automatic listing creation from consignment items
        * Multi-image upload to eBay
        * Inventory synchronization (Odoo ↔ eBay)
        * Order import from eBay to Odoo
        * Real-time status updates
        * Price and quantity synchronization
        * Automatic item state management

        Workflow:
        ---------
        1. Configure eBay API credentials
        2. Select consignment item to list
        3. System creates eBay listing with images
        4. Synchronize inventory automatically
        5. Import orders when sold on eBay
        6. Update item status to 'sold'
        7. Process commission and payout
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'consignment_core',
        'consignment_wallet',
        'sale_management',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/ebay_config_views.xml',
        'views/consignment_item_views.xml',
        'views/ebay_listing_views.xml',
        'views/ebay_order_views.xml',
        'views/ebay_menus.xml',

        # Wizards
        'wizard/ebay_list_item_wizard_views.xml',

        # Data
        'data/ir_cron.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
