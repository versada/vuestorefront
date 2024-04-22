from datetime import timedelta

from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from . import common


class TestQueryOrder(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_1 = cls.env.ref("sale.sale_order_1")
        # Make it owner of SO, otherwise search by partner_id.name
        # fails, because of access rights.
        cls.sale_1.partner_id = cls.user_portal.partner_id.id
        cls.sale_1.message_subscribe(partner_ids=[cls.user_portal.partner_id.id])
        cls.sale_1.order_line[0].name = 'my-line-name-1'

    def test_01_query_order(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrder($id: Int) {
                    order (id: $id) {
                        name
                    }
                }
                """,
                variables={"id": self.sale_1.id},
            )
        # THEN
        self.assertEqual(
            res["order"],
            {
                "name": self.sale_1.name,
            },
        )

    def test_02_query_orders_by_line_name_exact_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $lineName: String) {
                    orders(filter: {ids: $ids, lineName: $lineName}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "lineName": "my-line-name-1"},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    def test_03_query_orders_by_line_name_partial_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $lineName: String) {
                    orders(filter: {ids: $ids, lineName: $lineName}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "lineName": "my-line-name"},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    def test_04_query_orders_by_line_name_no_match(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $lineName: String) {
                    orders(filter: {ids: $ids, lineName: $lineName}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "lineName": "my-line-name-2"},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [])

    def test_05_query_orders_by_name(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $name: String) {
                    orders(filter: {ids: $ids, name: $name}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={"name": self.sale_1.name},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    # NOTE. stage here is actually state..
    def test_06_query_orders_by_stages(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $stages: [OrderStage]) {
                    orders(filter: {ids: $ids, stages: $stages}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "stages": ["Quotation"]},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    def test_07_query_orders_by_partner_name(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $partnerName: String) {
                    orders(filter: {ids: $ids, partnerName: $partnerName}) {
                        orders {
                            name
                        }
                    }
                }
                """,
                variables={
                    "ids": self.sale_1.ids, "partnerName": self.sale_1.partner_id.name
                },
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    def test_08_query_orders_by_date_from(self):
        # GIVEN
        dt = self.sale_1.date_order - timedelta(days=10)
        date_from = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $dateFrom: String) {
                    orders(filter: {ids: $ids, dateFrom: $dateFrom}) {
                        orders { name }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "dateFrom": date_from},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])

    def test_09_query_orders_by_date_to(self):
        # GIVEN
        dt = self.sale_1.date_order + timedelta(days=10)
        date_to = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrders($ids: [Int], $dateTo: String) {
                    orders(filter: {ids: $ids, dateTo: $dateTo}) {
                        orders { name }
                    }
                }
                """,
                variables={"ids": self.sale_1.ids, "dateTo": date_to},
            )
        # THEN
        self.assertEqual(res["orders"]["orders"], [{"name": self.sale_1.name}])
