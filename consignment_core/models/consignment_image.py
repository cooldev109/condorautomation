# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ConsignmentImage(models.Model):
    _name = 'consignment.image'
    _description = 'Consignment Item Image'
    _order = 'sequence, id'

    name = fields.Char(
        string='Description',
        help="Description of this photo"
    )

    consignment_item_id = fields.Many2one(
        'consignment.item',
        string='Consignment Item',
        required=True,
        ondelete='cascade',  # Delete images when item is deleted
        index=True
    )

    image = fields.Binary(
        string='Image',
        required=True,
        attachment=True,  # Store in ir_attachment for better performance
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Display order"
    )

    company_id = fields.Many2one(
        'res.company',
        related='consignment_item_id.company_id',
        store=True
    )
