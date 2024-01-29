# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import requests
from odoo import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    vsf_domain = fields.Char(string="Domain for VSF")
    vsf_payment_success_return_url = fields.Char(
        'Payment Success Return Url', required=True, translate=True, default='Dummy'
    )
    vsf_payment_error_return_url = fields.Char(
        'Payment Error Return Url', required=True, translate=True, default='Dummy'
    )
    vsf_mailing_list_id = fields.Many2one('mailing.list', 'Newsletter', domain=[('is_public', '=', True)])

    def get_vsf_http_domain(self):
        self.ensure_one()
        # Using same logic as standard `_get_http_domain`
        if not self.vsf_domain:
            return ''
        domain = self.vsf_domain
        if not domain.startswith('http'):
            domain = 'http://%s' % domain
        return domain.rstrip('/')

    @api.model
    def enable_b2c_reset_password(self):
        """ Enable sign up and reset password on default website """
        website = self.env.ref('website.default_website', raise_if_not_found=False)
        if website:
            website.auth_signup_uninvited = 'b2c'

        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('auth_signup.invitation_scope', 'b2c')
        ICP.set_param('auth_signup.reset_password', True)


class WebsiteRewrite(models.Model):
    _inherit = 'website.rewrite'

    def _get_vsf_tags(self):
        tags = 'WR%s' % self.id
        return tags

    def _vsf_request_cache_invalidation(self):
        ICP = self.env['ir.config_parameter'].sudo()
        url = ICP.get_param('vsf_cache_invalidation_url', False)
        key = ICP.get_param('vsf_cache_invalidation_key', False)

        if url and key:
            try:
                for website_rewrite in self:
                    tags = website_rewrite._get_vsf_tags()

                    # Make the GET request to the /cache-invalidate
                    requests.get(url, params={'key': key, 'tags': tags}, timeout=5)
            except:
                pass

    def write(self, vals):
        res = super(WebsiteRewrite, self).write(vals)
        self._vsf_request_cache_invalidation()
        return res

    def unlink(self):
        self._vsf_request_cache_invalidation()
        return super(WebsiteRewrite, self).unlink()
