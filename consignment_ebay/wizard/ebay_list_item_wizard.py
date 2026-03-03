# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EbayListItemWizard(models.TransientModel):
    _name = 'ebay.list.item.wizard'
    _description = 'List Item on eBay Wizard'

    consignment_item_id = fields.Many2one(
        'consignment.item',
        string='Consignment Item',
        required=True,
        readonly=True
    )

    # Listing Details
    title = fields.Char(
        string='Title',
        required=True,
        help='eBay listing title (max 80 characters)'
    )

    description = fields.Html(
        string='Description',
        required=True
    )

    # Category & Condition
    category_id = fields.Char(
        string='eBay Category ID',
        required=True,
        help='Find category IDs at https://www.ebay.com/sh/sellhub/create-listing'
    )

    condition_id = fields.Selection([
        ('1000', 'New'),
        ('1500', 'New Other'),
        ('2000', 'Manufacturer Refurbished'),
        ('2500', 'Seller Refurbished'),
        ('3000', 'Used'),
        ('7000', 'For Parts or Not Working'),
    ], string='Condition', required=True)

    # Pricing
    currency_id = fields.Many2one(
        'res.currency',
        related='consignment_item_id.currency_id',
        string='Currency'
    )

    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        required=True
    )

    # Listing Settings
    listing_type = fields.Selection([
        ('FixedPriceItem', 'Fixed Price'),
    ], string='Listing Type', default='FixedPriceItem', required=True)

    duration = fields.Selection([
        ('Days_7', '7 Days'),
        ('Days_30', '30 Days'),
        ('GTC', 'Good Till Cancelled'),
    ], string='Duration', default='GTC', required=True)

    quantity = fields.Integer(
        string='Quantity',
        default=1,
        required=True
    )

    # Auto-publish
    auto_publish = fields.Boolean(
        string='Publish Immediately',
        default=True,
        help='If checked, listing will be published to eBay immediately'
    )

    @api.onchange('consignment_item_id')
    def _onchange_consignment_item(self):
        """Pre-fill fields from consignment item"""
        if self.consignment_item_id:
            # Create title from description (max 80 chars)
            desc = self.consignment_item_id.description or ''
            self.title = (desc[:77] + '...') if len(desc) > 80 else desc

            # Set description
            self.description = f"""
            <h3>{self.title}</h3>
            <p><strong>Condition:</strong> {dict(self.consignment_item_id._fields['condition'].selection).get(self.consignment_item_id.condition)}</p>
            <p><strong>Serial/Part Number:</strong> {self.consignment_item_id.serial_number or 'N/A'}</p>
            <br/>
            <p>{self.consignment_item_id.description}</p>
            """

            # Set price
            self.price = self.consignment_item_id.listing_price

            # Map condition
            condition_map = {
                'new': '1000',
                'used': '3000',
                'refurbished': '2000',
                'for_parts': '7000',
            }
            self.condition_id = condition_map.get(self.consignment_item_id.condition, '3000')

            # Get category from item if set
            if self.consignment_item_id.ebay_category_id:
                self.category_id = self.consignment_item_id.ebay_category_id

    def action_create_listing(self):
        """Create eBay listing"""
        self.ensure_one()

        # Create listing record
        listing = self.env['ebay.listing'].create({
            'name': self.title,
            'consignment_item_id': self.consignment_item_id.id,
            'description': self.description,
            'category_id': self.category_id,
            'condition_id': self.condition_id,
            'price': self.price,
            'quantity': self.quantity,
            'listing_type': self.listing_type,
            'duration': self.duration,
        })

        # Create inventory item and offer on eBay
        listing.action_create_inventory_item()

        # Publish if requested
        if self.auto_publish:
            listing.action_publish_to_ebay()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ebay.listing',
            'res_id': listing.id,
            'view_mode': 'form',
            'target': 'current',
        }
