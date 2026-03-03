# -*- coding: utf-8 -*-

import logging
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ConsignmentPortal(CustomerPortal):

    @http.route(['/my/test'], type='http', auth="user", website=True)
    def test_controller(self, **kw):
        """Test route to verify controller is loaded"""
        _logger.info("========== TEST ROUTE CALLED - CONTROLLER IS WORKING! ==========")
        return "Controller is loaded!"

    @http.route(['/my/counters'], type='json', auth="user", website=True)
    def counters(self, counters, **kw):
        """Override counters to use our _prepare_home_portal_values"""
        _logger.info("========== COUNTERS ROUTE CALLED ==========")
        return self._prepare_home_portal_values(counters)

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """Override home to use our portal values"""
        _logger.info("========== HOME ROUTE CALLED ==========")
        values = self._prepare_portal_layout_values()
        return request.render("portal.portal_my_home", values)

    def _prepare_home_portal_values(self, counters):
        """Add consignment data to portal home"""
        _logger.info("========== CONSIGNMENT PORTAL: _prepare_home_portal_values CALLED ==========")
        _logger.info("Counters requested: %s", counters)

        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        _logger.info("Current user: %s (ID: %s)", request.env.user.name, request.env.user.id)
        _logger.info("Partner: %s (ID: %s)", partner.name, partner.id)

        # Check access rights
        has_item_access = request.env['consignment.item'].check_access_rights('read', raise_exception=False)
        has_wallet_access = request.env['consignment.wallet'].check_access_rights('read', raise_exception=False)

        _logger.info("Has item access: %s", has_item_access)
        _logger.info("Has wallet access: %s", has_wallet_access)

        # Always calculate consignment counts
        if has_item_access:
            item_count = request.env['consignment.item'].search_count([('owner_id', '=', partner.id)])
            _logger.info("Found %s consignment items for partner %s", item_count, partner.name)
            values['consignment_count'] = item_count
        else:
            _logger.warning("No access to consignment.item model!")
            values['consignment_count'] = 0

        if has_wallet_access:
            wallet_count = request.env['consignment.wallet'].search_count([('owner_id', '=', partner.id)])
            _logger.info("Found %s wallets for partner %s", wallet_count, partner.name)
            values['wallet_count'] = wallet_count
        else:
            _logger.warning("No access to consignment.wallet model!")
            values['wallet_count'] = 0

        _logger.info("Final values being returned: %s", values)
        _logger.info("========== CONSIGNMENT PORTAL: END ==========")

        return values

    # ===========================
    # My Consignment Items
    # ===========================

    @http.route(['/my/consignment', '/my/consignment/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_consignment_items(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        """Display user's consignment items"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ConsignmentItem = request.env['consignment.item']

        domain = [('owner_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'received': {'label': _('Received'), 'domain': [('state', '=', 'received')]},
            'listed': {'label': _('Listed'), 'domain': [('state', '=', 'listed')]},
            'sold': {'label': _('Sold'), 'domain': [('state', '=', 'sold')]},
            'paid': {'label': _('Paid'), 'domain': [('state', '=', 'paid')]},
            'returned': {'label': _('Returned'), 'domain': [('state', '=', 'returned')]},
        }

        # Default sort and filter
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # Count for pager
        item_count = ConsignmentItem.search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/consignment",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=item_count,
            page=page,
            step=self._items_per_page
        )

        # Get items
        items = ConsignmentItem.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'items': items,
            'page_name': 'consignment',
            'pager': pager,
            'default_url': '/my/consignment',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })

        return request.render("consignment_core.portal_my_consignment_items", values)

    @http.route(['/my/consignment/<int:item_id>'], type='http', auth="user", website=True)
    def portal_consignment_item_detail(self, item_id, access_token=None, **kw):
        """Display single consignment item detail"""
        try:
            item_sudo = self._document_check_access('consignment.item', item_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'page_name': 'consignment',
            'item': item_sudo,
        }
        return request.render("consignment_core.portal_consignment_item_detail", values)

    # ===========================
    # My Wallet
    # ===========================

    @http.route(['/my/wallet'], type='http', auth="user", website=True)
    def portal_my_wallet(self, **kw):
        """Display user's wallet information"""
        partner = request.env.user.partner_id
        Wallet = request.env['consignment.wallet']

        # Get or create wallet
        wallet = Wallet.search([('owner_id', '=', partner.id)], limit=1)

        if not wallet:
            return request.render("consignment_core.portal_no_wallet", {
                'page_name': 'wallet',
            })

        values = {
            'page_name': 'wallet',
            'wallet': wallet,
            'transactions': wallet.transaction_ids.sorted(key=lambda r: r.create_date, reverse=True),
        }
        return request.render("consignment_core.portal_my_wallet", values)

    @http.route(['/my/transactions', '/my/transactions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_transactions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """Display user's wallet transactions"""
        partner = request.env.user.partner_id
        Wallet = request.env['consignment.wallet']
        Transaction = request.env['consignment.wallet.transaction']

        wallet = Wallet.search([('owner_id', '=', partner.id)], limit=1)

        if not wallet:
            return request.redirect('/my/wallet')

        domain = [('wallet_id', '=', wallet.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'date_old': {'label': _('Oldest'), 'order': 'create_date asc'},
            'amount': {'label': _('Amount'), 'order': 'amount desc'},
        }

        # Default sort
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Count for pager
        transaction_count = Transaction.search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/transactions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=transaction_count,
            page=page,
            step=self._items_per_page
        )

        # Get transactions
        transactions = Transaction.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values = {
            'page_name': 'transactions',
            'wallet': wallet,
            'transactions': transactions,
            'pager': pager,
            'default_url': '/my/transactions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        }

        return request.render("consignment_core.portal_my_transactions", values)
