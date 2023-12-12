from unittest.mock import MagicMock, patch

from ..schemas import order
from . import common


class TestQueryMutateOrder(common.TestVuestorefrontSaleCommon):
    def test_01_query_order(self):
        # GIVEN
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getOrder($id: Int) {
                    order(id: $id) {
                        name
                        clientOrderRef
                        orderLines {
                            product {
                                name
                            }
                        }
                    }
                }
                """,
                variables={"id": self.sale_1.id},
            )
        # THEN
        order_lines = res["order"].pop("orderLines")
        self.assertEqual(
            res["order"],
            {
                "name": self.sale_1.name,
                "clientOrderRef": None,
            },
        )
        self.assertEqual(order_lines[0]["product"]["name"], "Pedal Bin")

    @patch.object(order, "request", MagicMock())
    def test_02_mutate_order(self):
        # GIVEN
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation {
                    updateOrder(
                        data: {
                            clientOrderRef: "abc123"
                        }
                    ) {
                        id
                        clientOrderRef
                    }
                }
                """,
            )
        # THEN
        self.assertEqual(
            res["updateOrder"],
            {"id": self.sale_1.id, "clientOrderRef": "abc123"},
        )
        self.assertEqual(self.sale_1.client_order_ref, "abc123")
