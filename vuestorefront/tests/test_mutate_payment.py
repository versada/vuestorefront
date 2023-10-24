from unittest.mock import patch

from .common import TestVuestorefrontSaleCommon

PATH_PATCH_PAYMENT_REQ = "odoo.addons.vuestorefront.schemas.payment.request"


class TestMutatePayment(TestVuestorefrontSaleCommon):
    @patch(PATH_PATCH_PAYMENT_REQ)
    def test_01_mutate_pay_transfer(self, req1):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation MakePayment ($acquirerId: Int!) {
                    makePayment(
                        acquirerId: $acquirerId
                    ) { id }
                }
                """,
                variables={"acquirerId": self.payment_acquirer_transfer.id}
            )
        # THEN
        transaction = self.PaymentTransaction.browse(
            res["makePayment"]["id"]
        )
        self.assertEqual(transaction.sale_order_ids, self.sale_1)
        self.assertEqual(self.sale_1.state, 'sent')
