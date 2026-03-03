# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EbayConfig(models.Model):
    _name = 'ebay.config'
    _description = 'eBay Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(
        string='Configuration Name',
        required=True,
        default='eBay Configuration'
    )

    # API Credentials
    app_id = fields.Char(
        string='App ID (Client ID)',
        required=True,
        help='eBay Application ID from Developer Portal'
    )

    cert_id = fields.Char(
        string='Cert ID (Client Secret)',
        required=True,
        help='eBay Certificate ID from Developer Portal'
    )

    dev_id = fields.Char(
        string='Dev ID',
        help='eBay Developer ID (optional for some endpoints)'
    )

    # OAuth Tokens
    access_token = fields.Char(
        string='Access Token',
        readonly=True,
        help='OAuth 2.0 access token'
    )

    refresh_token = fields.Char(
        string='Refresh Token',
        readonly=True,
        help='OAuth 2.0 refresh token for getting new access tokens'
    )

    token_expiry = fields.Datetime(
        string='Token Expiry',
        readonly=True,
        help='When the current access token expires'
    )

    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production (Live)'),
    ], string='Environment', default='sandbox', required=True)

    # eBay Site
    site_id = fields.Selection([
        ('0', 'United States'),
        ('2', 'Canada (English)'),
        ('3', 'United Kingdom'),
        ('15', 'Australia'),
        ('71', 'France'),
        ('77', 'Germany'),
        ('100', 'eBay Motors'),
        ('186', 'Spain'),
        ('201', 'Hong Kong'),
    ], string='eBay Site', default='0', required=True)

    # Default Settings
    default_listing_duration = fields.Selection([
        ('Days_1', '1 Day'),
        ('Days_3', '3 Days'),
        ('Days_5', '5 Days'),
        ('Days_7', '7 Days'),
        ('Days_10', '10 Days'),
        ('Days_30', '30 Days'),
        ('GTC', 'Good Till Cancelled'),
    ], string='Default Duration', default='GTC', required=True)

    default_condition_id = fields.Selection([
        ('1000', 'New'),
        ('1500', 'New Other'),
        ('2000', 'Manufacturer Refurbished'),
        ('2500', 'Seller Refurbished'),
        ('3000', 'Used'),
        ('7000', 'For Parts or Not Working'),
    ], string='Default Condition', default='3000')

    default_listing_type = fields.Selection([
        ('FixedPriceItem', 'Fixed Price'),
        ('Auction', 'Auction'),
    ], string='Default Listing Type', default='FixedPriceItem', required=True)

    default_dispatch_time = fields.Integer(
        string='Default Dispatch Time (days)',
        default=3,
        help='Number of business days to ship after payment'
    )

    # Category Settings
    default_category_id = fields.Char(
        string='Default eBay Category ID',
        help='eBay category number (e.g., 11804 for CNC equipment)'
    )

    # Shipping Settings
    default_shipping_service = fields.Selection([
        ('USPSPriority', 'USPS Priority Mail'),
        ('USPSPriorityFlatRate', 'USPS Priority Flat Rate'),
        ('UPSGround', 'UPS Ground'),
        ('FedExHomeDelivery', 'FedEx Home Delivery'),
        ('FreightShipping', 'Freight'),
    ], string='Default Shipping Service', default='FreightShipping')

    default_shipping_cost = fields.Float(
        string='Default Shipping Cost',
        default=0.0,
        help='Set to 0 for calculated shipping or free shipping'
    )

    # Payment Settings
    paypal_email = fields.Char(
        string='PayPal Email',
        help='PayPal email for receiving payments'
    )

    accept_paypal = fields.Boolean(
        string='Accept PayPal',
        default=True
    )

    # Returns Policy
    returns_accepted = fields.Boolean(
        string='Returns Accepted',
        default=True
    )

    return_period = fields.Selection([
        ('Days_14', '14 Days'),
        ('Days_30', '30 Days'),
        ('Days_60', '60 Days'),
    ], string='Return Period', default='Days_30')

    refund_option = fields.Selection([
        ('MoneyBack', 'Money Back'),
        ('MoneyBackOrExchange', 'Money Back or Exchange'),
    ], string='Refund Option', default='MoneyBack')

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(default=True)

    # OAuth Redirect URI (auto-computed from base URL)
    redirect_uri = fields.Char(
        string='OAuth Redirect URI',
        compute='_compute_redirect_uri',
        store=False,
        help='Copy this URL into the eBay Developer Portal → OAuth Redirect URI field.'
    )

    # Status
    is_connected = fields.Boolean(
        string='Connected to eBay',
        compute='_compute_is_connected',
        store=True
    )

    last_sync_date = fields.Datetime(
        string='Last Sync',
        readonly=True
    )

    def _compute_redirect_uri(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
        for record in self:
            record.redirect_uri = f"{base_url}/ebay/oauth/callback"

    @api.depends('access_token', 'token_expiry')
    def _compute_is_connected(self):
        """Check if we have valid authentication"""
        for record in self:
            record.is_connected = bool(
                record.access_token and
                record.token_expiry and
                record.token_expiry > fields.Datetime.now()
            )

    def action_test_connection(self):
        """Test eBay API connection"""
        self.ensure_one()
        ebay_api = self.env['ebay.api'].with_context(ebay_config_id=self.id)
        try:
            result = ebay_api.test_connection()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': _('Connected to eBay successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_('Connection failed: %s') % str(e))

    def action_refresh_token(self):
        """Manually refresh the access token"""
        self.ensure_one()
        ebay_api = self.env['ebay.api'].with_context(ebay_config_id=self.id)
        try:
            ebay_api.refresh_access_token()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': _('Access token refreshed!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_('Token refresh failed: %s') % str(e))

    def action_get_oauth_url(self):
        """Get OAuth authorization URL"""
        self.ensure_one()
        ebay_api = self.env['ebay.api'].with_context(ebay_config_id=self.id)
        auth_url = ebay_api.get_oauth_url()

        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'new',
        }
