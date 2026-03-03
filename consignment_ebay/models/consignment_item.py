# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsignmentItem(models.Model):
    _inherit = 'consignment.item'

    # eBay Integration
    ebay_listing_ids = fields.One2many(
        'ebay.listing',
        'consignment_item_id',
        string='eBay Listings'
    )

    ebay_listing_count = fields.Integer(
        string='eBay Listings',
        compute='_compute_ebay_listing_count'
    )

    is_on_ebay = fields.Boolean(
        string='Listed on eBay',
        compute='_compute_is_on_ebay',
        store=True
    )

    ebay_category_id = fields.Char(
        string='eBay Category',
        help='eBay category ID for this type of equipment'
    )

    @api.depends('ebay_listing_ids')
    def _compute_ebay_listing_count(self):
        for record in self:
            record.ebay_listing_count = len(record.ebay_listing_ids)

    @api.depends('ebay_listing_ids.state')
    def _compute_is_on_ebay(self):
        for record in self:
            record.is_on_ebay = any(
                listing.state == 'listed'
                for listing in record.ebay_listing_ids
            )

    def action_list_on_ebay(self):
        """Open wizard to list item on eBay"""
        self.ensure_one()

        if self.state not in ['received', 'listed']:
            raise UserError(_('Item must be received before listing on eBay'))

        if not self.listing_price:
            raise UserError(_('Please set a listing price first'))

        if not self.image_ids:
            raise UserError(_('Please add at least one photo before listing on eBay'))

        return {
            'name': _('List on eBay'),
            'type': 'ir.actions.act_window',
            'res_model': 'ebay.list.item.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consignment_item_id': self.id,
            }
        }

    def action_view_ebay_listings(self):
        """View eBay listings for this item"""
        self.ensure_one()

        return {
            'name': _('eBay Listings'),
            'type': 'ir.actions.act_window',
            'res_model': 'ebay.listing',
            'view_mode': 'tree,form',
            'domain': [('consignment_item_id', '=', self.id)],
            'context': {'default_consignment_item_id': self.id}
        }

    def action_sync_from_ebay(self):
        """Sync status from eBay for active listings"""
        self.ensure_one()

        active_listings = self.ebay_listing_ids.filtered(lambda l: l.state == 'listed')
        if not active_listings:
            raise UserError(_('No active eBay listings to sync'))

        # TODO: Implement sync logic
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _('Synced %d listing(s) from eBay') % len(active_listings),
                'type': 'success',
                'sticky': False,
            }
        }
