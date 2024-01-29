# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.http import request
from odoo import api, models, _
from odoo.addons.auth_signup.models.res_partner import now
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def api_action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = self.env.ref('vuestorefront.website_reset_password_email')

        assert template._name == 'mail.template'

        website = request.env['website'].get_current_website()
        domain = website.get_vsf_http_domain()
        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False
        }
        template.write(template_values)

        for user in self:
            token = user.signup_token
            signup_url = "%s/forgot-password/new-password?token=%s" % (domain, token)
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                template.with_context(lang=user.lang, signup_url=signup_url).send_mail(user.id, force_send=not create_mode, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    @api.model
    def prepare_vsf_signup_vals(self, name, login, password, **kw):
        vals = {
            'name': name,
            'login': login,
            'password': password,
        }
        if 'vat' in kw:
            vals['vat'] = kw['vat']
        return vals
