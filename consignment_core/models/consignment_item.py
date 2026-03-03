# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ConsignmentItem(models.Model):
    _name = 'consignment.item'
    _description = 'Consignment Item'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'intake_date desc, id desc'

    # ===========================
    # BASIC INFORMATION
    # ===========================
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help="Unique reference for this consignment item"
    )

    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        tracking=True,
        help="Customer who owns this item"
    )

    serial_number = fields.Char(
        string='Serial/Part Number',
        tracking=True,
        help="Original manufacturer serial or part number"
    )

    description = fields.Text(
        string='Description',
        required=True,
        tracking=True,
        help="Detailed description of the item"
    )

    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used - Good'),
        ('refurbished', 'Refurbished'),
        ('for_parts', 'For Parts/Not Working'),
    ], string='Condition', default='used', required=True, tracking=True)

    notes = fields.Text(
        string='Internal Notes',
        help="Internal notes not visible to customer"
    )

    # ===========================
    # IMAGES
    # ===========================
    image_ids = fields.One2many(
        'consignment.image',
        'consignment_item_id',
        string='Images',
        help="Upload multiple photos"
    )

    image_count = fields.Integer(
        string='Image Count',
        compute='_compute_image_count'
    )

    # ===========================
    # PRICING
    # ===========================
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    expected_price = fields.Monetary(
        string='Expected Price',
        currency_field='currency_id',
        help="Customer's hoped-for selling price"
    )

    listing_price = fields.Monetary(
        string='Listing Price',
        currency_field='currency_id',
        tracking=True,
        help="Actual price listed for sale"
    )

    sale_price = fields.Monetary(
        string='Sale Price',
        currency_field='currency_id',
        tracking=True,
        help="Final price sold for"
    )

    commission_rate = fields.Float(
        string='Commission %',
        default=20.0,
        help="Commission percentage for this sale"
    )

    commission_amount = fields.Monetary(
        string='Commission Amount',
        currency_field='currency_id',
        compute='_compute_commission',
        store=True,
        help="Commission amount in currency"
    )

    net_amount = fields.Monetary(
        string='Net Amount to Owner',
        currency_field='currency_id',
        compute='_compute_commission',
        store=True,
        help="Amount credited to owner after commission"
    )

    # ===========================
    # DATES
    # ===========================
    intake_date = fields.Date(
        string='Intake Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )

    listed_date = fields.Datetime(
        string='Listed Date',
        readonly=True,
        help="When item was published for sale"
    )

    sold_date = fields.Datetime(
        string='Sold Date',
        readonly=True,
        help="When item was marked as sold"
    )

    returned_date = fields.Datetime(
        string='Returned Date',
        readonly=True,
        help="When item was returned to owner"
    )

    return_reason = fields.Selection([
        ('defective', 'Defective/Not Working'),
        ('customer_return', 'Customer Returned'),
        ('unsold', 'Unsold - Owner Request'),
        ('damaged', 'Damaged'),
        ('other', 'Other'),
    ], string='Return Reason', help='Reason for returning item to owner')

    return_notes = fields.Text(
        string='Return Notes',
        help='Additional details about the return'
    )

    acquisition_type = fields.Selection([
        ('consignment', 'Consignment'),
        ('purchase', 'Direct Purchase'),
    ], string='Acquisition Type', default='consignment', required=True,
       help='How the item was acquired: on consignment or purchased outright')

    # ===========================
    # STATE WORKFLOW
    # ===========================
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('listed', 'Listed for Sale'),
        ('sold', 'Sold'),
        ('paid', 'Paid to Owner'),
        ('returned', 'Returned to Owner'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # ===========================
    # PRODUCT & INVENTORY
    # ===========================
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
        help="Auto-created product linked to this item"
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        default=lambda self: self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Current Location',
        domain=[('usage', '=', 'internal')],
        help="Current storage location"
    )

    # ===========================
    # LINKS TO OTHER MODULES
    # ===========================
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        readonly=True,
        help="If sold through Odoo sale order"
    )

    ebay_listing_id = fields.Char(
        string='eBay Listing ID',
        readonly=True,
        help="eBay listing identifier"
    )

    # ===========================
    # COMPANY
    # ===========================
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # ===========================
    # COMPUTE METHODS
    # ===========================
    @api.depends('image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.image_ids)

    @api.depends('sale_price', 'commission_rate')
    def _compute_commission(self):
        for record in self:
            if record.sale_price and record.commission_rate:
                record.commission_amount = record.sale_price * (record.commission_rate / 100)
                record.net_amount = record.sale_price - record.commission_amount
            else:
                record.commission_amount = 0.0
                record.net_amount = 0.0

    # ===========================
    # CRUD METHODS
    # ===========================
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('consignment.item') or _('New')
        return super().create(vals_list)

    # ===========================
    # ACTION METHODS (BUTTONS)
    # ===========================
    def action_receive(self):
        """Mark item as received and create product"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft items can be received!"))

            # Create product if not exists
            if not record.product_id:
                product = self.env['product.product'].create({
                    'name': f"{record.description[:50]} - {record.name}",
                    'type': 'product',  # Stockable
                    'categ_id': self.env.ref('product.product_category_all').id,
                    'list_price': record.expected_price or 0.0,
                    'standard_price': 0.0,  # No cost for consignment
                    'detailed_type': 'product',
                    'description_sale': record.description,
                })
                record.product_id = product.id

            record.write({
                'state': 'received',
                'intake_date': fields.Date.context_today(self),
            })

            # Post message to chatter
            record.message_post(
                body=_("Item received and product created."),
                subject=_("Item Received")
            )

    def action_list(self):
        """Mark item as listed for sale"""
        for record in self:
            if record.state != 'received':
                raise UserError(_("Only received items can be listed!"))
            if not record.listing_price:
                raise UserError(_("Please set a listing price first!"))

            record.write({
                'state': 'listed',
                'listed_date': fields.Datetime.now(),
            })

            record.message_post(
                body=_("Item listed for sale at %s") % record.listing_price,
                subject=_("Item Listed")
            )

    def action_mark_sold(self):
        """Mark item as sold"""
        for record in self:
            if record.state != 'listed':
                raise UserError(_("Only listed items can be marked as sold!"))
            if not record.sale_price:
                raise UserError(_("Please set the sale price first!"))

            record.write({
                'state': 'sold',
                'sold_date': fields.Datetime.now(),
            })

            record.message_post(
                body=_("Item sold for %s. Commission: %s. Net to owner: %s") % (
                    record.sale_price,
                    record.commission_amount,
                    record.net_amount
                ),
                subject=_("Item Sold!")
            )

    def action_mark_paid(self):
        """Mark item as paid to owner"""
        for record in self:
            if record.state != 'sold':
                raise UserError(_("Only sold items can be marked as paid!"))

            record.write({
                'state': 'paid',
            })

            record.message_post(
                body=_("Owner has been credited with %s") % record.net_amount,
                subject=_("Payment Processed")
            )

    def action_return(self):
        """Return item to owner"""
        for record in self:
            if record.state not in ['received', 'listed']:
                raise UserError(_("Only received or listed items can be returned to owner!"))

            record.write({
                'state': 'returned',
                'returned_date': fields.Datetime.now(),
            })

            record.message_post(
                body=_("Item returned to %s") % record.owner_id.name,
                subject=_("Returned to Owner")
            )

    def action_cancel(self):
        """Cancel the consignment item"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_("Cannot cancel a paid item!"))

            record.write({
                'state': 'cancelled',
            })

            record.message_post(
                body=_("Consignment item cancelled."),
                subject=_("Cancelled")
            )

    def action_view_images(self):
        """Action to view images"""
        self.ensure_one()
        return {
            'name': _('Images'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'consignment.image',
            'domain': [('consignment_item_id', '=', self.id)],
            'context': {'default_consignment_item_id': self.id}
        }
