from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def prepare_vsf_vals(self, data):
        # Only used for current session user current order.
        self.ensure_one()
        vals = {}
        if "client_order_ref" in data:
            vals["client_order_ref"] = data["client_order_ref"]
        return vals
