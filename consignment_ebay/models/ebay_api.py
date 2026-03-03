# -*- coding: utf-8 -*-
import requests
import json
import base64
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class EbayAPI(models.AbstractModel):
    """eBay API Helper - handles all API communication"""
    _name = 'ebay.api'
    _description = 'eBay API Helper'

    # API Endpoints
    SANDBOX_ENDPOINTS = {
        'auth': 'https://auth.sandbox.ebay.com/oauth2/authorize',
        'token': 'https://api.sandbox.ebay.com/identity/v1/oauth2/token',
        'trading': 'https://api.sandbox.ebay.com/ws/api.dll',
        'sell': 'https://api.sandbox.ebay.com/sell',
    }

    PRODUCTION_ENDPOINTS = {
        'auth': 'https://auth.ebay.com/oauth2/authorize',
        'token': 'https://api.ebay.com/identity/v1/oauth2/token',
        'trading': 'https://api.ebay.com/ws/api.dll',
        'sell': 'https://api.ebay.com/sell',
    }

    def _get_config(self):
        """Get eBay configuration"""
        config_id = self.env.context.get('ebay_config_id')
        if config_id:
            return self.env['ebay.config'].browse(config_id)

        # Get default active config
        config = self.env['ebay.config'].search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True),
        ], limit=1)

        if not config:
            raise UserError(_('No eBay configuration found. Please configure eBay integration first.'))

        return config

    def _get_endpoints(self):
        """Get API endpoints based on environment"""
        config = self._get_config()
        if config.environment == 'sandbox':
            return self.SANDBOX_ENDPOINTS
        return self.PRODUCTION_ENDPOINTS

    def _get_auth_header(self):
        """Get authorization header with valid token"""
        config = self._get_config()

        # Check if token is expired
        if not config.access_token or not config.token_expiry or config.token_expiry <= fields.Datetime.now():
            if config.refresh_token:
                self.refresh_access_token()
            else:
                raise UserError(_('Please authorize eBay access first. Go to eBay Configuration and click "Get OAuth URL".'))

        return {
            'Authorization': f'Bearer {config.access_token}',
            'Content-Type': 'application/json',
        }

    def get_oauth_url(self):
        """Generate OAuth authorization URL"""
        config = self._get_config()
        endpoints = self._get_endpoints()

        # For simplicity, using user consent flow
        # In production, you'd redirect to a callback URL
        scopes = [
            'https://api.ebay.com/oauth/api_scope',
            'https://api.ebay.com/oauth/api_scope/sell.inventory',
            'https://api.ebay.com/oauth/api_scope/sell.marketing',
            'https://api.ebay.com/oauth/api_scope/sell.account',
            'https://api.ebay.com/oauth/api_scope/sell.fulfillment',
        ]

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
        redirect_uri = f"{base_url}/ebay/oauth/callback"

        params = {
            'client_id': config.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
        }

        url = endpoints['auth'] + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
        return url

    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        config = self._get_config()
        endpoints = self._get_endpoints()

        # Create authorization header
        credentials = f"{config.app_id}:{config.cert_id}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {b64_credentials}',
        }

        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069') + '/ebay/oauth/callback',
        }

        try:
            response = requests.post(endpoints['token'], headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()

            # Save tokens
            config.write({
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'token_expiry': datetime.now() + timedelta(seconds=token_data['expires_in']),
            })

            _logger.info('eBay OAuth tokens obtained successfully')
            return token_data

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to exchange code for token: {e}')
            raise UserError(_('Failed to get access token: %s') % str(e))

    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        config = self._get_config()
        endpoints = self._get_endpoints()

        if not config.refresh_token:
            raise UserError(_('No refresh token available. Please authorize again.'))

        credentials = f"{config.app_id}:{config.cert_id}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {b64_credentials}',
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': config.refresh_token,
            'scope': 'https://api.ebay.com/oauth/api_scope',
        }

        try:
            response = requests.post(endpoints['token'], headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()

            # Update tokens
            config.write({
                'access_token': token_data['access_token'],
                'token_expiry': datetime.now() + timedelta(seconds=token_data['expires_in']),
            })

            _logger.info('eBay access token refreshed successfully')
            return True

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to refresh token: {e}')
            raise UserError(_('Failed to refresh token: %s') % str(e))

    def test_connection(self):
        """Test API connection"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        # Test with a simple API call (get user info)
        url = f"{endpoints['sell']}/account/v1/privilege"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            _logger.info('eBay API connection test successful')
            return response.json()

        except requests.exceptions.RequestException as e:
            _logger.error(f'eBay API connection test failed: {e}')
            raise UserError(_('Connection test failed: %s') % str(e))

    def create_or_replace_inventory_item(self, sku, product_data):
        """Create or update an inventory item"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        url = f"{endpoints['sell']}/inventory/v1/inventory_item/{sku}"

        try:
            response = requests.put(url, headers=headers, json=product_data)
            response.raise_for_status()
            _logger.info(f'Inventory item {sku} created/updated successfully')
            return response.status_code == 204  # 204 No Content on success

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to create inventory item: {e}')
            if hasattr(e.response, 'text'):
                _logger.error(f'Response: {e.response.text}')
            raise UserError(_('Failed to create inventory item: %s') % str(e))

    def create_offer(self, sku, offer_data):
        """Create an offer for an inventory item"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        url = f"{endpoints['sell']}/inventory/v1/offer"

        try:
            response = requests.post(url, headers=headers, json=offer_data)
            response.raise_for_status()
            result = response.json()
            _logger.info(f'Offer created for SKU {sku}: {result.get("offerId")}')
            return result

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to create offer: {e}')
            if hasattr(e.response, 'text'):
                _logger.error(f'Response: {e.response.text}')
            raise UserError(_('Failed to create offer: %s') % str(e))

    def publish_offer(self, offer_id):
        """Publish an offer to eBay"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        url = f"{endpoints['sell']}/inventory/v1/offer/{offer_id}/publish"

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            _logger.info(f'Offer {offer_id} published: {result.get("listingId")}')
            return result

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to publish offer: {e}')
            if hasattr(e.response, 'text'):
                _logger.error(f'Response: {e.response.text}')
            raise UserError(_('Failed to publish offer: %s') % str(e))

    def upload_image(self, image_data):
        """Upload image to eBay"""
        # Note: eBay recommends hosting images externally and providing URLs
        # For simplicity, we'll include images as data URLs in the inventory item
        # In production, consider using eBay's image upload API or external hosting
        return f"data:image/jpeg;base64,{image_data}"

    def get_orders(self, limit=50):
        """Get recent orders from eBay"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        url = f"{endpoints['sell']}/fulfillment/v1/order"
        params = {'limit': limit}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get orders: {e}')
            raise UserError(_('Failed to get orders: %s') % str(e))

    def end_listing(self, offer_id):
        """End/delist an offer"""
        headers = self._get_auth_header()
        endpoints = self._get_endpoints()

        url = f"{endpoints['sell']}/inventory/v1/offer/{offer_id}/withdraw"

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            _logger.info(f'Offer {offer_id} ended successfully')
            return True

        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to end listing: {e}')
            raise UserError(_('Failed to end listing: %s') % str(e))
