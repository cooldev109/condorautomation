# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EbayListing(models.Model):
    _name = 'ebay.listing'
    _description = 'eBay Listing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Listing Title',
        required=True,
        tracking=True
    )

    # Links
    consignment_item_id = fields.Many2one(
        'consignment.item',
        string='Consignment Item',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    product_id = fields.Many2one(
        'product.product',
        related='consignment_item_id.product_id',
        store=True,
        string='Product'
    )

    owner_id = fields.Many2one(
        'res.partner',
        related='consignment_item_id.owner_id',
        store=True,
        string='Owner'
    )

    # eBay Identifiers
    sku = fields.Char(
        string='SKU',
        required=True,
        copy=False,
        help='Unique identifier for this listing'
    )

    offer_id = fields.Char(
        string='eBay Offer ID',
        readonly=True,
        tracking=True
    )

    listing_id = fields.Char(
        string='eBay Listing ID',
        readonly=True,
        tracking=True,
        help='eBay item ID (visible to buyers)'
    )

    ebay_url = fields.Char(
        string='eBay URL',
        compute='_compute_ebay_url',
        store=True
    )

    # Listing Details
    description = fields.Html(
        string='Description',
        required=True
    )

    category_id = fields.Char(
        string='eBay Category ID',
        required=True
    )

    condition_id = fields.Selection([
        ('1000', 'New'),
        ('1500', 'New Other'),
        ('2000', 'Manufacturer Refurbished'),
        ('2500', 'Seller Refurbished'),
        ('3000', 'Used'),
        ('7000', 'For Parts or Not Working'),
    ], string='Condition', required=True, default='3000')

    # Pricing
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        required=True,
        tracking=True
    )

    quantity = fields.Integer(
        string='Quantity',
        default=1,
        required=True
    )

    # Listing Settings
    listing_type = fields.Selection([
        ('FixedPriceItem', 'Fixed Price'),
        ('Auction', 'Auction'),
    ], string='Listing Type', default='FixedPriceItem', required=True)

    duration = fields.Selection([
        ('Days_1', '1 Day'),
        ('Days_3', '3 Days'),
        ('Days_5', '5 Days'),
        ('Days_7', '7 Days'),
        ('Days_10', '10 Days'),
        ('Days_30', '30 Days'),
        ('GTC', 'Good Till Cancelled'),
    ], string='Duration', default='GTC', required=True)

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('listed', 'Listed on eBay'),
        ('sold', 'Sold'),
        ('ended', 'Ended'),
        ('error', 'Error'),
    ], string='Status', default='draft', required=True, tracking=True)

    error_message = fields.Text(
        string='Error Message',
        readonly=True
    )

    # Dates
    listed_date = fields.Datetime(
        string='Listed Date',
        readonly=True
    )

    sold_date = fields.Datetime(
        string='Sold Date',
        readonly=True
    )

    ended_date = fields.Datetime(
        string='Ended Date',
        readonly=True
    )

    # Stats
    view_count = fields.Integer(
        string='Views',
        readonly=True,
        help='Number of views on eBay'
    )

    watcher_count = fields.Integer(
        string='Watchers',
        readonly=True,
        help='Number of watchers on eBay'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.depends('listing_id', 'company_id')
    def _compute_ebay_url(self):
        """Generate eBay listing URL"""
        for record in self:
            if record.listing_id:
                # US site by default
                record.ebay_url = f"https://www.ebay.com/itm/{record.listing_id}"
            else:
                record.ebay_url = False

    @api.model
    def create(self, vals):
        """Generate SKU if not provided"""
        if not vals.get('sku'):
            consignment_item = self.env['consignment.item'].browse(vals['consignment_item_id'])
            safe_name = consignment_item.name.replace('/', '-').replace(' ', '-')
            vals['sku'] = f"CONS-{safe_name}"
        return super().create(vals)

    def action_create_inventory_item(self):
        """Create inventory item on eBay"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_('Can only create inventory for draft listings'))

        ebay_api = self.env['ebay.api']

        # Prepare product data
        product_data = self._prepare_inventory_data()

        try:
            # Create inventory item
            ebay_api.create_or_replace_inventory_item(self.sku, product_data)

            # Create offer
            offer_data = self._prepare_offer_data()
            offer_result = ebay_api.create_offer(self.sku, offer_data)

            self.write({
                'offer_id': offer_result.get('offerId'),
                'state': 'draft',
            })

            self.message_post(body=_('Inventory item and offer created on eBay'))

        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise

    def action_publish_to_ebay(self):
        """Publish listing to eBay"""
        self.ensure_one()

        if not self.offer_id:
            raise UserError(_('Please create inventory item first'))

        ebay_api = self.env['ebay.api']

        try:
            # Publish offer
            result = ebay_api.publish_offer(self.offer_id)

            self.write({
                'listing_id': result.get('listingId'),
                'state': 'listed',
                'listed_date': fields.Datetime.now(),
            })

            # Update consignment item
            self.consignment_item_id.write({
                'ebay_listing_id': result.get('listingId'),
                'state': 'listed',
                'listed_date': fields.Datetime.now(),
            })

            self.message_post(body=_('Published to eBay! Listing ID: %s') % result.get('listingId'))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': _('Listed on eBay successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise

    def action_end_listing(self):
        """End eBay listing"""
        self.ensure_one()

        if self.state != 'listed':
            raise UserError(_('Can only end active listings'))

        ebay_api = self.env['ebay.api']

        try:
            ebay_api.end_listing(self.offer_id)

            self.write({
                'state': 'ended',
                'ended_date': fields.Datetime.now(),
            })

            self.message_post(body=_('Listing ended on eBay'))

        except Exception as e:
            raise UserError(_('Failed to end listing: %s') % str(e))

    def action_view_on_ebay(self):
        """Open eBay listing in browser"""
        self.ensure_one()
        if not self.ebay_url:
            raise UserError(_('No eBay URL available'))

        return {
            'type': 'ir.actions.act_url',
            'url': self.ebay_url,
            'target': 'new',
        }

    def _prepare_inventory_data(self):
        """Prepare inventory item data for eBay API"""
        self.ensure_one()
        import re

        # Strip HTML tags from description
        raw_desc = self.description or self.consignment_item_id.description or self.name
        clean_desc = re.sub(r'<[^>]+>', ' ', str(raw_desc)).strip() if raw_desc else self.name

        data = {
            'product': {
                'title': self.name[:80],  # eBay max title length
                'description': clean_desc[:4000],
                'aspects': {},
            },
            'condition': self.condition_id,
            'availability': {
                'shipToLocationAvailability': {
                    'quantity': self.quantity
                }
            }
        }

        return data

    def _prepare_offer_data(self):
        """Prepare offer data for eBay API"""
        self.ensure_one()

        data = {
            'sku': self.sku,
            'marketplaceId': 'EBAY_US',  # Change based on site
            'format': self.listing_type,
            'listingDuration': self.duration,
            'pricingSummary': {
                'price': {
                    'value': str(self.price),
                    'currency': self.currency_id.name
                }
            },
            'listingPolicies': {
                'fulfillmentPolicyId': 'default',  # Would be set from config
                'paymentPolicyId': 'default',
                'returnPolicyId': 'default',
            },
            'categoryId': self.category_id,
        }

        return data
