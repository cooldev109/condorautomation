# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsignmentIntakeWizard(models.TransientModel):
    _name = 'consignment.intake.wizard'
    _description = 'Consignment Intake Wizard'

    # Header fields (common for all items)
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        domain=[('is_consignment_owner', '=', True)],
        help='Customer who owns all items in this intake batch'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        default=lambda self: self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1),
        help='Warehouse where items will be stored'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Default Location',
        help='Default storage location for all items'
    )
    intake_date = fields.Date(
        string='Intake Date',
        default=fields.Date.context_today,
        required=True,
        help='Date when items were received'
    )
    commission_rate = fields.Float(
        string='Commission Rate (%)',
        default=20.0,
        help='Default commission rate for all items'
    )

    # Item lines
    line_ids = fields.One2many(
        'consignment.intake.wizard.line',
        'wizard_id',
        string='Items to Intake'
    )

    # Summary fields
    total_items = fields.Integer(
        string='Total Items',
        compute='_compute_totals',
        store=True
    )
    total_expected_value = fields.Monetary(
        string='Total Expected Value',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    @api.depends('line_ids', 'line_ids.expected_price')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_items = len(wizard.line_ids)
            wizard.total_expected_value = sum(wizard.line_ids.mapped('expected_price'))

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        """Set default location based on warehouse"""
        if self.warehouse_id:
            # Try to find a consignment-specific location, otherwise use lot stock location
            consignment_location = self.env['stock.location'].search([
                ('location_id', '=', self.warehouse_id.lot_stock_id.id),
                ('name', 'ilike', 'consignment')
            ], limit=1)

            if consignment_location:
                self.location_id = consignment_location
            else:
                self.location_id = self.warehouse_id.lot_stock_id

    def action_add_item(self):
        """Add a new blank line for item entry"""
        self.ensure_one()
        self.env['consignment.intake.wizard.line'].create({
            'wizard_id': self.id,
            'commission_rate': self.commission_rate,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'consignment.intake.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_items(self):
        """Create consignment items from wizard lines"""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('Please add at least one item before creating.'))

        items_created = []
        ConsignmentItem = self.env['consignment.item']

        for line in self.line_ids:
            # Validate required fields
            if not line.description:
                raise UserError(_('Description is required for all items.'))

            # Prepare item values
            item_vals = {
                'owner_id': self.owner_id.id,
                'serial_number': line.serial_number,
                'description': line.description,
                'condition': line.condition,
                'warehouse_id': self.warehouse_id.id,
                'location_id': line.location_id.id or self.location_id.id,
                'expected_price': line.expected_price,
                'listing_price': line.listing_price,
                'commission_rate': line.commission_rate,
                'intake_date': self.intake_date,
                'notes': line.notes,
            }

            # Create the item
            item = ConsignmentItem.create(item_vals)

            # Automatically receive the item (transition from draft to received)
            item.action_receive()

            items_created.append(item.id)

        # Prepare success message
        message = _('%d consignment item(s) created and received successfully!') % len(items_created)

        # Return action to show created items
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Consignment Items'),
            'res_model': 'consignment.item',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', items_created)],
            'context': {
                'default_owner_id': self.owner_id.id,
                'default_warehouse_id': self.warehouse_id.id,
            },
            'target': 'current',
        }


class ConsignmentIntakeWizardLine(models.TransientModel):
    _name = 'consignment.intake.wizard.line'
    _description = 'Consignment Intake Wizard Line'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'consignment.intake.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=10)

    # Item details
    serial_number = fields.Char(string='Serial/Part Number')
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the item'
    )
    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used - Good'),
        ('refurbished', 'Refurbished'),
        ('for_parts', 'For Parts/Not Working'),
    ], string='Condition', default='used', required=True)

    location_id = fields.Many2one(
        'stock.location',
        string='Specific Location',
        help='Override default location for this item'
    )

    # Pricing
    currency_id = fields.Many2one(
        related='wizard_id.currency_id',
        string='Currency'
    )
    expected_price = fields.Monetary(
        string='Expected Price',
        currency_field='currency_id',
        help='Price customer expects to get from sale'
    )
    listing_price = fields.Monetary(
        string='Listing Price',
        currency_field='currency_id',
        help='Price to list the item for'
    )
    commission_rate = fields.Float(
        string='Commission %',
        default=20.0,
        help='Commission rate for this item'
    )

    # Notes
    notes = fields.Text(string='Internal Notes')

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        """Auto-calculate listing price based on expected price"""
        if self.expected_price and not self.listing_price:
            # Suggest listing price 10% higher than expected price
            self.listing_price = self.expected_price * 1.1
