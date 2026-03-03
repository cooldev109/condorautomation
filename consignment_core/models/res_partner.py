# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_consignment_owner = fields.Boolean(
        string='Is Consignment Owner',
        help='Check if this partner consigns items to sell'
    )

    consignment_item_ids = fields.One2many(
        'consignment.item',
        'owner_id',
        string='Consignment Items',
        help='Items owned by this partner'
    )

    consignment_item_count = fields.Integer(
        string='Item Count',
        compute='_compute_consignment_item_count',
        help='Number of consignment items'
    )

    @api.depends('consignment_item_ids')
    def _compute_consignment_item_count(self):
        """Count consignment items for this owner"""
        for partner in self:
            partner.consignment_item_count = len(partner.consignment_item_ids)
