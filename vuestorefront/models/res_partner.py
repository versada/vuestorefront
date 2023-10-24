from odoo import models, api
from odoo.osv import expression

VSF_ADDRESS_DIRECT_FIELDS = [
    'name', ''
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def prepare_vsf_address_direct_fields(self):
        return [
            "name",
            "street",
            "street2",
            "phone",
            "zip",
            "city",
            "state_id",
            "country_id",
            "email",
        ]

    @api.model
    def prepare_vsf_address_vals(self, address):
        vals = {}
        for fname in self.prepare_vsf_address_direct_fields():
            if fname in address:
                vals[fname] = address[fname]
        return vals

    def prepare_vsf_invoice_address_domain(self):
        self.ensure_one()
        return [("type", "=", "invoice")]

    def prepare_vsf_delivery_address_domain(self):
        self.ensure_one()
        return [("type", "=", "delivery")]

    def _prepare_vsf_base_address_domain(self):
        self.ensure_one()
        return [("id", "child_of", self.commercial_partner_id.ids)]

    def _prepare_vsf_address_domain(self, address_types):
        self.ensure_one()
        base_domain = self._prepare_vsf_base_address_domain()
        types = [at.value for at in address_types]
        type_domains = []
        for addr_type in types:
            method_name = f"prepare_vsf_{addr_type}_address_domain"
            type_domains.append(getattr(self, method_name)())
        return expression.AND([base_domain, expression.OR(type_domains)])
