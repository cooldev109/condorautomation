from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ConsignmentWallet(models.Model):
    _name = 'consignment.wallet'
    _description = 'Consignment Owner Wallet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'owner_id'

    # Basic Information
    name = fields.Char(
        string='Wallet Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        ondelete='restrict',
        domain=[('is_consignment_owner', '=', True)],
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    active = fields.Boolean(
        default=True,
        tracking=True
    )

    # Balance Information
    balance = fields.Monetary(
        string='Current Balance',
        currency_field='currency_id',
        compute='_compute_balance',
        store=True,
        tracking=True
    )
    pending_commission = fields.Monetary(
        string='Pending Commission',
        currency_field='currency_id',
        compute='_compute_pending_commission',
        help='Commission from sold items not yet marked as paid'
    )
    total_earned = fields.Monetary(
        string='Total Earned',
        currency_field='currency_id',
        compute='_compute_totals',
        help='Total commission earned (all time)'
    )
    total_paid_out = fields.Monetary(
        string='Total Paid Out',
        currency_field='currency_id',
        compute='_compute_totals',
        help='Total amount paid out to owner (all time)'
    )

    # Relations
    transaction_ids = fields.One2many(
        'consignment.wallet.transaction',
        'wallet_id',
        string='Transactions'
    )
    item_ids = fields.Many2many(
        'consignment.item',
        compute='_compute_item_ids',
        string='Consignment Items'
    )

    # Statistics
    transaction_count = fields.Integer(
        compute='_compute_transaction_count',
        string='Transaction Count'
    )
    item_count = fields.Integer(
        compute='_compute_item_count',
        string='Item Count'
    )

    # SQL Constraints
    _sql_constraints = [
        ('owner_company_unique',
         'UNIQUE(owner_id, company_id)',
         'Each owner can only have one wallet per company!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('consignment.wallet') or _('New')
        return super().create(vals)

    @api.depends('owner_id')
    def _compute_item_ids(self):
        """Find all consignment items for this wallet's owner"""
        for wallet in self:
            if wallet.owner_id:
                items = self.env['consignment.item'].search([
                    ('owner_id', '=', wallet.owner_id.id)
                ])
                wallet.item_ids = items
            else:
                wallet.item_ids = False

    @api.depends('transaction_ids.amount', 'transaction_ids.transaction_type')
    def _compute_balance(self):
        """Calculate current wallet balance from all transactions"""
        for wallet in self:
            credit_transactions = wallet.transaction_ids.filtered(
                lambda t: t.transaction_type in ['commission', 'adjustment_credit']
            )
            debit_transactions = wallet.transaction_ids.filtered(
                lambda t: t.transaction_type in ['payout', 'adjustment_debit']
            )

            total_credit = sum(credit_transactions.mapped('amount'))
            total_debit = sum(debit_transactions.mapped('amount'))
            wallet.balance = total_credit - total_debit

    @api.depends('owner_id')
    def _compute_pending_commission(self):
        """Calculate commission from sold items not yet paid"""
        for wallet in self:
            if not wallet.owner_id:
                wallet.pending_commission = 0.0
                continue

            # Find sold items for this owner
            sold_items = self.env['consignment.item'].search([
                ('owner_id', '=', wallet.owner_id.id),
                ('state', '=', 'sold')
            ])

            # Sum up net amounts
            total = sum(sold_items.mapped('net_amount'))
            wallet.pending_commission = total

    @api.depends('transaction_ids.amount', 'transaction_ids.transaction_type')
    def _compute_totals(self):
        """Calculate total earned and paid out amounts"""
        for wallet in self:
            commission_transactions = wallet.transaction_ids.filtered(
                lambda t: t.transaction_type == 'commission'
            )
            payout_transactions = wallet.transaction_ids.filtered(
                lambda t: t.transaction_type == 'payout'
            )

            wallet.total_earned = sum(commission_transactions.mapped('amount'))
            wallet.total_paid_out = sum(payout_transactions.mapped('amount'))

    def _compute_transaction_count(self):
        for wallet in self:
            wallet.transaction_count = len(wallet.transaction_ids)

    def _compute_item_count(self):
        for wallet in self:
            wallet.item_count = len(wallet.item_ids)

    def action_view_transactions(self):
        """Open transaction list for this wallet"""
        self.ensure_one()
        return {
            'name': _('Wallet Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.wallet.transaction',
            'view_mode': 'tree,form',
            'domain': [('wallet_id', '=', self.id)],
            'context': {
                'default_wallet_id': self.id,
                'default_owner_id': self.owner_id.id,
            }
        }

    def action_view_items(self):
        """Open consignment items for this owner"""
        self.ensure_one()
        return {
            'name': _('Consignment Items'),
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.item',
            'view_mode': 'tree,form',
            'domain': [('owner_id', '=', self.owner_id.id)],
            'context': {
                'default_owner_id': self.owner_id.id,
            }
        }

    def action_create_payout(self):
        """Open payout wizard"""
        self.ensure_one()
        if self.balance <= 0:
            raise UserError(_('Cannot create payout: wallet balance is zero or negative.'))

        return {
            'name': _('Create Payout'),
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.payout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_wallet_id': self.id,
                'default_owner_id': self.owner_id.id,
                'default_amount': self.balance,
            }
        }

    @api.model
    def get_or_create_wallet(self, owner_id):
        """Get existing wallet or create new one for owner"""
        wallet = self.search([
            ('owner_id', '=', owner_id),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if not wallet:
            owner = self.env['res.partner'].browse(owner_id)
            wallet = self.create({
                'owner_id': owner_id,
                'name': f'WALLET/{owner.name}',
            })

        return wallet
