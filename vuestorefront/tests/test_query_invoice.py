from datetime import timedelta

from odoo.tests.common import tagged
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from . import common


@tagged('post_install', '-at_install')
class TestQueryInvoice(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice_1 = cls.env.ref("l10n_generic_coa.demo_invoice_1")
        cls.invoice_1.message_subscribe(partner_ids=[cls.user_portal.partner_id.id])
        cls.invoice_1.invoice_line_ids[0].name = 'my-line-name-1'

    def test_01_query_invoice(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoice($id: Int) {
                    invoice (id: $id) {
                        name
                        state
                        paymentState
                        invoiceOrigin
                        order { name }
                        ref
                    }
                }
                """,
                variables={"id": self.invoice_1.id},
            )
        # THEN
        self.assertEqual(
            res["invoice"],
            {
                "name": self.invoice_1.name,
                "state": "Posted",
                "paymentState": "NotPaid",
                "invoiceOrigin": None,
                "order": {"name": None},
                "ref": None,
            },
        )

    def test_02_query_invoices_by_line_name_exact_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $lineName: String) {
                    invoices(filter: {ids: $ids, lineName: $lineName}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "lineName": "my-line-name-1"},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_03_query_invoices_by_line_name_partial_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $lineName: String) {
                    invoices(filter: {ids: $ids, lineName: $lineName}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "lineName": "my-line-name"},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_04_query_invoices_by_line_name_no_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $lineName: String) {
                    invoices(filter: {ids: $ids, lineName: $lineName}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "lineName": "my-line-name-2"},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [])

    def test_05_query_invoices_by_name(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $name: String) {
                    invoices(filter: {ids: $ids, name: $name}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"name": self.invoice_1.name},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_06_query_invoices_by_states(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $states: [InvoiceState]) {
                    invoices(filter: {ids: $ids, states: $states}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "states": ["Posted"]},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_07_query_invoices_by_payment_state(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $paymentStates: [InvoicePaymentState]) {
                    invoices(filter: {ids: $ids, paymentStates: $paymentStates}) {
                        invoices {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "paymentState": ["NotPaid"]},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_08_query_invoices_by_date_from(self):
        # GIVEN
        dt = self.invoice_1.invoice_date - timedelta(days=10)
        date_from = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $dateFrom: String) {
                    invoices(filter: {ids: $ids, dateFrom: $dateFrom}) {
                        invoices { name }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "dateFrom": date_from},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])

    def test_09_query_invoices_by_date_to(self):
        # GIVEN
        dt = self.invoice_1.invoice_date + timedelta(days=10)
        date_to = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getInvoices($ids: [Int], $dateTo: String) {
                    invoices(filter: {ids: $ids, dateTo: $dateTo}) {
                        invoices { name }
                    }
                }
                """,
                variables={"ids": self.invoice_1.ids, "dateTo": date_to},
            )
        # THEN
        self.assertEqual(res["invoices"]["invoices"], [{"name": self.invoice_1.name}])
