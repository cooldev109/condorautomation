# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class EbayOrder(models.Model):
    _name = 'ebay.order'
    _description = 'eBay Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'order_date desc'

    name = fields.Char(
        string='Order Number',
        required=True,
        copy=False,
        readonly=True,
        tracking=True
    )

    # eBay Info
    ebay_order_id = fields.Char(
        string='eBay Order ID',
        required=True,
        readonly=True,
        index=True
    )

    ebay_listing_id = fields.Many2one(
        'ebay.listing',
        string='eBay Listing',
        readonly=True
    )

    consignment_item_id = fields.Many2one(
        'consignment.item',
        related='ebay_listing_id.consignment_item_id',
        store=True,
        string='Consignment Item'
    )

    # Buyer Info
    buyer_username = fields.Char(
        string='Buyer Username',
        readonly=True
    )

    buyer_email = fields.Char(
        string='Buyer Email',
        readonly=True
    )

    # Pricing
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True
    )

    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        readonly=True
    )

    # Dates
    order_date = fields.Datetime(
        string='Order Date',
        required=True,
        readonly=True
    )

    payment_date = fields.Datetime(
        string='Payment Date',
        readonly=True
    )

    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', tracking=True)

    # Odoo Integration
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
        help='Created sale order in Odoo'
    )

    imported = fields.Boolean(
        string='Imported to Odoo',
        default=False,
        readonly=True
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    def action_import_to_odoo(self):
        """Create sale order in Odoo from eBay order"""
        self.ensure_one()

        if self.imported:
            raise UserError(_('Order already imported'))

        if not self.ebay_listing_id:
            raise UserError(_('No listing linked to this order'))

        # Create/get customer
        partner = self._get_or_create_partner()

        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': self.order_date,
            'origin': f"eBay Order: {self.name}",
            'note': f"Imported from eBay. Order ID: {self.ebay_order_id}",
        })

        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.consignment_item_id.product_id.id,
            'product_uom_qty': 1,
            'price_unit': self.total_amount,
        })

        # Confirm order
        sale_order.action_confirm()

        # Update consignment item
        self.consignment_item_id.write({
            'sale_order_line_id': sale_order.order_line[0].id,
            'state': 'sold',
            'sold_date': fields.Datetime.now(),
            'sale_price': self.total_amount,
        })

        # Update this record
        self.write({
            'sale_order_id': sale_order.id,
            'imported': True,
            'status': 'completed',
        })

        self.message_post(body=_('Imported to Odoo. Sale Order: %s') % sale_order.name)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_or_create_partner(self):
        """Get or create partner from eBay buyer info"""
        self.ensure_one()

        # Search for existing partner
        partner = self.env['res.partner'].search([
            ('email', '=', self.buyer_email)
        ], limit=1)

        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.buyer_username or 'eBay Buyer',
                'email': self.buyer_email,
                'customer_rank': 1,
                'comment': f"eBay customer. Username: {self.buyer_username}",
            })

        return partner

    @api.model
    def cron_import_ebay_orders(self):
        """Scheduled action to import orders from eBay"""
        ebay_api = self.env['ebay.api']

        try:
            orders_data = ebay_api.get_orders(limit=50)

            for order_data in orders_data.get('orders', []):
                self._process_ebay_order(order_data)

            _logger.info(f"Imported {len(orders_data.get('orders', []))} orders from eBay")

        except Exception as e:
            _logger.error(f"Failed to import eBay orders: {e}")

    def _process_ebay_order(self, order_data):
        """Process a single eBay order"""
        ebay_order_id = order_data.get('orderId')

        # Check if already imported
        existing = self.search([('ebay_order_id', '=', ebay_order_id)], limit=1)
        if existing:
            return existing

        # Find matching listing
        listing_id = order_data.get('lineItems', [{}])[0].get('listingMarketplaceId')
        listing = self.env['ebay.listing'].search([
            ('listing_id', '=', listing_id)
        ], limit=1)

        # Create order record
        order = self.create({
            'name': ebay_order_id,
            'ebay_order_id': ebay_order_id,
            'ebay_listing_id': listing.id if listing else False,
            'buyer_username': order_data.get('buyer', {}).get('username'),
            'buyer_email': order_data.get('buyer', {}).get('email'),
            'total_amount': float(order_data.get('pricingSummary', {}).get('total', {}).get('value', 0)),
            'currency_id': self.env['res.currency'].search([
                ('name', '=', order_data.get('pricingSummary', {}).get('total', {}).get('currency', 'USD'))
            ], limit=1).id,
            'order_date': order_data.get('creationDate'),
            'status': 'paid' if order_data.get('orderPaymentStatus') == 'PAID' else 'pending',
        })

        return order
