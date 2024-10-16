from datetime import date

from odoo import models, api
from odoo.osv import expression

from ..utils import date_string_to_datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def prepare_vsf_vals(self, data):
        # Only used for current session user current order.
        self.ensure_one()
        vals = {}
        if "client_order_ref" in data:
            vals["client_order_ref"] = data["client_order_ref"]
        return vals

    @api.model
    def prepare_vsf_domain(self, commercial_partner_id, **kw):
        domain = [("message_partner_ids", "child_of", [commercial_partner_id])]
        if kw.get("ids"):
            domain.append(("id", "in", kw["ids"]))
        # TODO: rename this to states?
        if kw.get('stages'):
            states = [stage.value for stage in kw['stages']]
            domain.append(('state', 'in', states))
        if kw.get('invoice_status'):
            invoice_status = [
                invoice_status.value for invoice_status in kw['invoice_status']
            ]
            domain.append(('invoice_status', 'in', invoice_status))
        if kw.get("name"):
            domain.append(("name", "ilike", kw["name"]))
        if kw.get("partner_name"):
            domain.append(("partner_id.name", "ilike", kw["partner_name"]))
        if kw.get("date_from"):
            domain.append(self._get_vsf_date_from_leaf(kw["date_from"]))
        if kw.get("date_to"):
            domain.append(self._get_vsf_date_to_leaf(kw["date_to"]))
        if kw.get("line_name"):
            domain.append(("order_line.name", "ilike", kw["line_name"]))
        if kw.get("is_expired") is not None:
            domain = expression.AND(
                [domain, self._get_vsf_is_expired_domain(kw["is_expired"])]
            )
        return domain

    def _get_vsf_date_from_leaf(self, date_from):
        dt = date_string_to_datetime(date_from)
        return ("date_order", ">=", dt)

    def _get_vsf_date_to_leaf(self, date_to):
        dt = date_string_to_datetime(date_to, hour=23, minute=59, second=59)
        return ("date_order", "<=", dt)

    def _get_vsf_is_expired_domain(self, is_expired):
        today = date.today()
        if is_expired:
            return [("validity_date", "!=", False), ("validity_date", "<", today)]
        return ["|", ("validity_date", "=", False), ("validity_date", ">=", today)]
