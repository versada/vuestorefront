from odoo import models, fields, api, _
from odoo.osv import expression


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def prepare_vsf_domain(self, sale_order, website, **kw):
        domain = expression.AND(
            [
                [
                    '&',
                    ('vsf_active', '=', True),
                    ('state', 'in', ['enabled', 'test'])
                ],
                [
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', sale_order.company_id.id)
                ],
                [
                    '|',
                    ('website_id', '=', False),
                    ('website_id', '=', website.id)
                ],
                [
                    '|',
                    ('country_ids', '=', False),
                    ('country_ids', 'in', [sale_order.partner_id.country_id.id])
                ]
            ]
        )
        if kw.get('included_providers'):
            domain = expression.AND(
                [domain, [('provider', 'in', kw['included_providers'])]]
            )
        if kw.get('excluded_providers'):
            domain = expression.AND(
                [domain, [('provider', 'not in', kw['excluded_providers'])]]
            )
        return domain
