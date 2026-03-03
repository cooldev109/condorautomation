from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ConsignmentWalletTransaction(models.Model):
    _name = 'consignment.wallet.transaction'
    _description = 'Consignment Wallet Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Basic Information
    name = fields.Char(
        string='Transaction Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    date = fields.Date(
        string='Transaction Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    wallet_id = fields.Many2one(
        'consignment.wallet',
        string='Wallet',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        related='wallet_id.owner_id',
        store=True,
        readonly=True
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

    # Transaction Details
    transaction_type = fields.Selection([
        ('commission', 'Commission Earned'),
        ('payout', 'Payout to Owner'),
        ('adjustment_credit', 'Adjustment (Credit)'),
        ('adjustment_debit', 'Adjustment (Debit)'),
    ], string='Transaction Type', required=True, tracking=True)

    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True,
        tracking=True
    )
    description = fields.Text(
        string='Description',
        tracking=True
    )
    notes = fields.Text(
        string='Internal Notes'
    )

    # Related Documents
    consignment_item_id = fields.Many2one(
        'consignment.item',
        string='Related Item',
        ondelete='set null',
        help='Consignment item that generated this transaction (for commission entries)'
    )
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ], string='Payment Method', help='For payout transactions')

    payment_reference = fields.Char(
        string='Payment Reference',
        help='Check number, transfer reference, etc.'
    )

    # Computed Fields
    wallet_balance_after = fields.Monetary(
        string='Balance After',
        currency_field='currency_id',
        compute='_compute_balance_after',
        store=True,
        help='Wallet balance after this transaction'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'consignment.wallet.transaction'
            ) or _('New')
        return super().create(vals)

    @api.depends('wallet_id.balance', 'date', 'amount', 'transaction_type')
    def _compute_balance_after(self):
        """Calculate wallet balance after this transaction"""
        for transaction in self:
            if not transaction.wallet_id:
                transaction.wallet_balance_after = 0.0
                continue

            # For new records (not yet saved), calculate from current wallet balance
            # We can't use ID in database searches for NewId records
            if not transaction._origin or not transaction._origin.id:
                # New record - start from current wallet balance
                current_balance = transaction.wallet_id.balance

                # Apply this transaction to the balance
                if transaction.transaction_type in ['commission', 'adjustment_credit']:
                    transaction.wallet_balance_after = current_balance + transaction.amount
                elif transaction.transaction_type in ['payout', 'adjustment_debit']:
                    transaction.wallet_balance_after = current_balance - transaction.amount
                else:
                    transaction.wallet_balance_after = current_balance
            else:
                # Existing record - get all transactions up to this one (by date and id)
                previous_transactions = self.search([
                    ('wallet_id', '=', transaction.wallet_id.id),
                    '|',
                    ('date', '<', transaction.date),
                    '&',
                    ('date', '=', transaction.date),
                    ('id', '<=', transaction.id)
                ])

                balance = 0.0
                for trans in previous_transactions:
                    if trans.transaction_type in ['commission', 'adjustment_credit']:
                        balance += trans.amount
                    elif trans.transaction_type in ['payout', 'adjustment_debit']:
                        balance -= trans.amount

                transaction.wallet_balance_after = balance

    @api.constrains('amount')
    def _check_amount(self):
        """Ensure amount is positive"""
        for transaction in self:
            if transaction.amount <= 0:
                raise ValidationError(_('Transaction amount must be positive!'))

    # NOTE: Balance validation is done in the payout wizard (action_create_payout)
    # before creating the transaction. A constraint here would incorrectly include
    # the new transaction itself in the balance calculation, causing false negatives.

    @api.model
    def create_commission_transaction(self, item):
        """Create a commission transaction for a paid consignment item"""
        if not item.owner_id:
            raise UserError(_('Cannot create commission transaction: item has no owner.'))

        if item.net_amount <= 0:
            raise UserError(_('Cannot create commission transaction: owner commission is zero or negative.'))

        # Get or create wallet
        wallet = self.env['consignment.wallet'].get_or_create_wallet(item.owner_id.id)

        # Create transaction
        transaction = self.create({
            'wallet_id': wallet.id,
            'transaction_type': 'commission',
            'amount': item.net_amount,
            'consignment_item_id': item.id,
            'description': f'Commission from item {item.name}: {item.description}',
            'date': fields.Date.context_today(self),
        })

        return transaction
