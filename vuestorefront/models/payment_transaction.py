# Copyright 2023 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PaymentTransactionInherit(models.Model):
    _inherit = "payment.transaction"

    created_on_vsf = fields.Boolean(string="Created on Vsf?", default=False)
