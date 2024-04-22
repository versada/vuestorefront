from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def prepare_vsf_domain(self, commercial_partner_id, **kw):
        domain = [("message_partner_ids", "child_of", [commercial_partner_id])]
        if kw.get("ids"):
            domain.append(("id", "in", kw["ids"]))
        if kw.get("name"):
            domain.append(("name", "ilike", kw["name"]))
        if kw.get("states"):
            domain.append(("state", "in", [state.value for state in kw["states"]]))
        if kw.get("payment_states"):
            domain.append(self._get_vsf_payment_state_leaf(kw["payment_states"]))
        if kw.get("date_from"):
            domain.append(self._get_vsf_date_from_leaf(kw["date_from"]))
        if kw.get("date_to"):
            domain.append(self._get_vsf_date_to_leaf(kw["date_to"]))
        if kw.get("line_name"):
            domain.append(("invoice_line_ids.name", "ilike", kw["line_name"]))
        return domain

    def convert_payment_state_to_vsf(self):
        self.ensure_one()
        state = self.payment_state
        if state == "in_payment":
            state = "paid"
        elif state == "invoicing_legacy":
            state = "not_paid"
        return state

    @api.model
    def _get_vsf_payment_state_leaf(self, vsf_payment_states):
        states = [state.value for state in vsf_payment_states]
        if "paid" in states:
            states.append("in_payment")
        return ("payment_state", "in", states)

    def _get_vsf_date_from_leaf(self, date_from):
        return ("invoice_date", ">=", date_from)

    def _get_vsf_date_to_leaf(self, date_to):
        return ("invoice_date", "<=", date_to)
