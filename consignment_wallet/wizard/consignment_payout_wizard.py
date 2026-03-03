from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ConsignmentPayoutWizard(models.TransientModel):
    _name = 'consignment.payout.wizard'
    _description = 'Consignment Payout Wizard'

    # Wallet Information
    wallet_id = fields.Many2one(
        'consignment.wallet',
        string='Wallet',
        required=True,
        readonly=True
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        related='wallet_id.owner_id',
        readonly=True
    )
    current_balance = fields.Monetary(
        string='Current Balance',
        related='wallet_id.balance',
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='wallet_id.currency_id',
        readonly=True
    )

    # Payout Details
    amount = fields.Monetary(
        string='Payout Amount',
        currency_field='currency_id',
        required=True
    )
    date = fields.Date(
        string='Payout Date',
        required=True,
        default=fields.Date.context_today
    )
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ], string='Payment Method', required=True, default='bank_transfer')

    payment_reference = fields.Char(
        string='Payment Reference',
        help='Check number, transfer reference, PayPal transaction ID, etc.'
    )
    description = fields.Text(
        string='Description',
        help='Optional description for this payout'
    )
    notes = fields.Text(
        string='Internal Notes',
        help='Internal notes (not visible to owner)'
    )

    @api.constrains('amount')
    def _check_amount(self):
        """Validate payout amount is positive"""
        for wizard in self:
            if wizard.amount <= 0:
                raise ValidationError(_('Payout amount must be positive!'))

    def action_create_payout(self):
        """Create payout transaction and update wallet"""
        self.ensure_one()

        # Manually calculate current balance from transactions
        # (Can't rely on computed field in same transaction due to ORM caching)
        credit_transactions = self.wallet_id.transaction_ids.filtered(
            lambda t: t.transaction_type in ['commission', 'adjustment_credit']
        )
        debit_transactions = self.wallet_id.transaction_ids.filtered(
            lambda t: t.transaction_type in ['payout', 'adjustment_debit']
        )

        total_credit = sum(credit_transactions.mapped('amount'))
        total_debit = sum(debit_transactions.mapped('amount'))
        fresh_balance = total_credit - total_debit

        # Validate amount
        if self.amount > fresh_balance:
            raise UserError(_(
                'Insufficient balance in wallet!\n'
                'Current balance: %(balance)s\n'
                'Transaction amount: %(amount)s'
            ) % {
                'balance': fresh_balance,
                'amount': self.amount
            })

        # Build description
        description = self.description or f'Payout to {self.owner_id.name}'

        # Create payout transaction
        transaction = self.env['consignment.wallet.transaction'].create({
            'wallet_id': self.wallet_id.id,
            'transaction_type': 'payout',
            'amount': self.amount,
            'date': self.date,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'description': description,
            'notes': self.notes,
        })

        # Post message to wallet
        self.wallet_id.message_post(
            body=_(
                'Payout created: %(amount)s<br/>'
                'Payment Method: %(method)s<br/>'
                'Reference: %(reference)s<br/>'
                'Transaction: %(transaction)s'
            ) % {
                'amount': f'{self.currency_id.symbol}{self.amount:.2f}',
                'method': dict(self._fields['payment_method'].selection).get(self.payment_method),
                'reference': self.payment_reference or 'N/A',
                'transaction': transaction.name
            }
        )

        # Return action to view the created transaction
        return {
            'name': _('Payout Transaction'),
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.wallet.transaction',
            'res_id': transaction.id,
            'view_mode': 'form',
            'target': 'current',
        }
