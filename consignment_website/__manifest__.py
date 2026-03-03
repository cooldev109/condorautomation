# -*- coding: utf-8 -*-
{
    'name': 'Consignment Website',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Industrial consignment platform portfolio website',
    'description': """
        CondorAutomation Portfolio Website
        ===================================
        Professional industrial consignment platform website
        - Homepage
        - Why Choose Us
        - Services
        - About Us
        - Contact
    """,
    'author': 'CondorAutomation',
    'website': 'https://www.condorautomation.com',
    'license': 'LGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        'views/templates.xml',
        'views/homepage.xml',
        'views/why_choose_us.xml',
        'views/services.xml',
        'views/about.xml',
        'views/contact.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'consignment_website/static/src/css/industrial_theme.css',
            'consignment_website/static/src/js/language_toggle.js',
            'consignment_website/static/src/js/translations.js',
            'consignment_website/static/src/js/carousel.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
