from unittest.mock import patch

from .common import TestVuestorefrontSaleCommon

PATH_PATCH_PAYMENT_REQ = "odoo.addons.vuestorefront.schemas.payment.request"


class TestMutatePayment(TestVuestorefrontSaleCommon):

    @patch(PATH_PATCH_PAYMENT_REQ)
    def test_01_query_payment_acquirer_transfer(self, req1):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getPaymentAcquirer ($id: Int) {
                    paymentAcquirer (id: $id) {
                        name
                        paymentMethods {
                            name
                            code
                            issuers {
                                name
                                code
                            }
                        }
                    }
                }
                """,
                variables={
                    "id": self.payment_acquirer_transfer.id,
                }
            )
        # THEN
        self.assertEqual(
            res["paymentAcquirer"],
            {
                "name": self.payment_acquirer_transfer.name,
                "paymentMethods": None
            }
        )

    @patch(PATH_PATCH_PAYMENT_REQ)
    def test_02_mutate_pay_transfer(self, req1):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation MakePayment (
                    $acquirerId: Int!, $extra: MakePaymentExtraInput
                ) {
                    makePayment(
                        acquirerId: $acquirerId
                        extra: $extra
                    ) {
                        id
                        returnUrl
                        checkoutUrl
                    }
                }
                """,
                variables={
                    "acquirerId": self.payment_acquirer_transfer.id,
                    "extra": {"returnUrl": "https://example.com/something"}
                }
            )
        # THEN
        transaction = self.PaymentTransaction.browse(
            res["makePayment"]["id"]
        )
        # transfer provider has no implementation for returnUrl, so
        # nothing is set on transaction.
        self.assertEqual(res["makePayment"]["returnUrl"], None)
        self.assertEqual(res["makePayment"]["checkoutUrl"], None)
        self.assertEqual(transaction.sale_order_ids, self.sale_1)
        self.assertEqual(self.sale_1.state, 'sent')
        transaction = self.sale_1.transaction_ids
        # No payments are done, only transfer payment option was registered.
        self.assertEqual(transaction.state, 'pending')
        self.assertFalse(transaction.payment_id)
