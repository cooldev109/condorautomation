# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ConsignmentWebsite(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.render('consignment_website.homepage')

    @http.route('/why-choose-us', type='http', auth='public', website=True)
    def why_choose_us(self, **kwargs):
        return request.render('consignment_website.why_choose_us')

    @http.route('/services', type='http', auth='public', website=True)
    def services(self, **kwargs):
        return request.render('consignment_website.services')

    @http.route('/about', type='http', auth='public', website=True)
    def about(self, **kwargs):
        return request.render('consignment_website.about')

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return request.render('consignment_website.contact')

    @http.route('/contact/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        """Handle contact form submission"""
        # Simple form handling - you can expand this later
        name = post.get('name', '')
        email = post.get('email', '')
        phone = post.get('phone', '')
        message = post.get('message', '')

        # For now, just return a thank you page
        # Later you can add email sending, CRM integration, etc.
        return request.render('consignment_website.contact_thank_you', {
            'name': name,
        })
