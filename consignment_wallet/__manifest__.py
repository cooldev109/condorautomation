{
    'name': 'Consignment Wallet',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Manage consignment owner wallets, commissions, and payouts',
    'description': """
        Consignment Wallet Management
        ==============================

        Features:
        ---------
        * Automatic wallet account creation for consignment owners
        * Commission tracking and automatic posting
        * Transaction history with detailed audit trail
        * Payout management with multiple payment methods
        * Balance reconciliation and reporting
        * Integration with consignment item sales workflow
    """,
    'depends': ['consignment_core', 'account'],
    'data': [
        'data/sequence_data.xml',
        'security/ir.model.access.csv',
        'views/consignment_wallet_views.xml',
        'views/consignment_wallet_transaction_views.xml',
        'views/consignment_wallet_menus.xml',
        'wizard/consignment_payout_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
