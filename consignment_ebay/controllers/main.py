# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class EbayOAuthController(http.Controller):

    @http.route('/ebay/oauth/callback', type='http', auth='user', methods=['GET'], csrf=False)
    def ebay_oauth_callback(self, **kwargs):
        """
        Handle eBay OAuth 2.0 callback.
        eBay redirects here after user authorizes access:
        /ebay/oauth/callback?code=XXXX  (success)
        /ebay/oauth/callback?error=XXXX (failure)
        """

        # eBay returned an error
        if kwargs.get('error'):
            error = kwargs.get('error', 'unknown_error')
            error_desc = kwargs.get('error_description', 'Authorization was denied or failed.')
            _logger.error('eBay OAuth error: %s - %s', error, error_desc)
            return self._render_result(
                success=False,
                message=f'eBay authorization failed: {error_desc}',
            )

        # Get the authorization code
        auth_code = kwargs.get('code')
        if not auth_code:
            _logger.error('eBay OAuth callback received no authorization code')
            return self._render_result(
                success=False,
                message='No authorization code received from eBay. Please try again.',
            )

        try:
            # Exchange the code for access + refresh tokens
            ebay_api = request.env['ebay.api']
            ebay_api.exchange_code_for_token(auth_code)
            _logger.info('eBay OAuth tokens saved successfully for company %s', request.env.company.name)

            return self._render_result(
                success=True,
                message='eBay connected successfully! Your access tokens have been saved.',
            )

        except Exception as e:
            _logger.error('Failed to exchange eBay authorization code for tokens: %s', str(e))
            return self._render_result(
                success=False,
                message=f'Failed to obtain tokens from eBay: {str(e)}',
            )

    def _render_result(self, success, message):
        """Return a simple HTML page with result and auto-redirect to Odoo backend."""
        color = '#28a745' if success else '#dc3545'
        icon = '&#10003;' if success else '&#10007;'
        title = 'Authorization Successful' if success else 'Authorization Failed'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>eBay OAuth - {title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f8f9fa;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 480px;
            width: 90%;
        }}
        .icon {{
            font-size: 60px;
            color: {color};
        }}
        h1 {{
            color: {color};
            margin: 16px 0;
            font-size: 24px;
        }}
        p {{
            color: #555;
            margin: 0 0 24px;
            line-height: 1.5;
        }}
        a {{
            display: inline-block;
            background: {color};
            color: white;
            padding: 10px 24px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
        }}
        a:hover {{ opacity: 0.85; }}
        .countdown {{
            color: #999;
            font-size: 13px;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">{icon}</div>
        <h1>{title}</h1>
        <p>{message}</p>
        <a href="/odoo">Return to Odoo</a>
        <p class="countdown" id="countdown">Redirecting in <span id="sec">5</span> seconds...</p>
    </div>
    <script>
        var sec = 5;
        var el = document.getElementById('sec');
        var interval = setInterval(function() {{
            sec--;
            el.textContent = sec;
            if (sec <= 0) {{
                clearInterval(interval);
                window.location.href = '/odoo';
            }}
        }}, 1000);
    </script>
</body>
</html>"""
        return request.make_response(html, headers=[('Content-Type', 'text/html')])
