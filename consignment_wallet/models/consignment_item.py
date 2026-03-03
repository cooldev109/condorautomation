from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ConsignmentItem(models.Model):
    _inherit = 'consignment.item'

    # Wallet Integration
    wallet_transaction_id = fields.Many2one(
        'consignment.wallet.transaction',
        string='Wallet Transaction',
        readonly=True,
        copy=False,
        help='Commission transaction created when item was marked as paid'
    )
    commission_posted = fields.Boolean(
        string='Commission Posted',
        compute='_compute_commission_posted',
        store=True,
        help='Indicates if commission has been posted to owner wallet'
    )

    @api.depends('wallet_transaction_id')
    def _compute_commission_posted(self):
        """Check if commission has been posted to wallet"""
        for item in self:
            item.commission_posted = bool(item.wallet_transaction_id)

    def action_mark_paid(self):
        """Override to automatically post commission to wallet"""
        res = super().action_mark_paid()

        # Post commission to wallet for each newly paid item
        for item in self:
            if item.state == 'paid' and not item.commission_posted:
                item._post_commission_to_wallet()

        return res

    def _post_commission_to_wallet(self):
        """Create wallet transaction for owner commission"""
        self.ensure_one()

        if self.commission_posted:
            raise UserError(_('Commission has already been posted for this item.'))

        if not self.owner_id:
            raise UserError(_('Cannot post commission: item has no owner.'))

        if self.net_amount <= 0:
            raise UserError(_('Cannot post commission: owner commission is zero or negative.'))

        # Create commission transaction
        transaction = self.env['consignment.wallet.transaction'].create_commission_transaction(self)

        # Link transaction to item
        self.wallet_transaction_id = transaction.id

        # Post message to item
        self.message_post(
            body=_(
                'Commission posted to wallet: %(amount)s<br/>'
                'Transaction: %(transaction)s'
            ) % {
                'amount': f'{self.currency_id.symbol}{self.net_amount:.2f}',
                'transaction': transaction.name
            }
        )

        return transaction

    def action_view_wallet_transaction(self):
        """Open the wallet transaction for this item"""
        self.ensure_one()
        if not self.wallet_transaction_id:
            raise UserError(_('No wallet transaction found for this item.'))

        return {
            'name': _('Wallet Transaction'),
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.wallet.transaction',
            'res_id': self.wallet_transaction_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
