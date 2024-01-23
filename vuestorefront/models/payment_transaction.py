from odoo import models, fields


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    checkout_url = fields.Char(
        help="URL to checkout to make payment. E.g external payments site."
    )

    def postprocess_vsf_payment_transaction(self, **kw):
        """Handle transaction after it was created from VSF payment.

        It is called in `make_payment` mutation, just after payment
        transaction (from sale order) is created.
        Intended to be extended for each payment acquirer that is used
        with VSF.
        """
        self.ensure_one()
        provider = self.acquirer_id.provider
        if provider == 'transfer':
            self._postprocess_vsf_payment_transaction_transfer(**kw)

    def handle_vsf_payment_update(self, **kw):
        """Handle payment manually if specific acquirer supports it.

        Intended to be used when payment was not fully processed by
        normal flow and we need to update payment using specific
        provider logic.

        Extend to implement update option for specific payment acquirer
        """
        self.ensure_one()

    def _postprocess_vsf_payment_transaction_transfer(self, **kw):
        self.ensure_one()
        data = {
            'return_url': self.return_url,
            'reference': self.reference,
            'amount': self.amount,
            'currency': self.currency_id.name,
        }
        # With transfer, we handle feedback immediately after transaction
        # was created, because there is no data exchange involved as with
        # real payment acquirer.
        self.sudo().form_feedback(data, 'transfer')
