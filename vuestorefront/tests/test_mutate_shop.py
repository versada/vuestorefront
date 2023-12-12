from unittest.mock import MagicMock, patch

from ..schemas import shop
from .common import TestVuestorefrontSaleCommon


class TestMutateShop(TestVuestorefrontSaleCommon):
    @patch.object(shop, "request", MagicMock())
    def test_01_mutate_add_to_cart(self):
        # GIVEN
        self.sale_1.order_line.unlink()
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation CartAddItem ($productId: Int!) {
                    cartAddItem(
                        productId: $productId
                        quantity: 10
                    ) {
                        order {
                            id
                        }
                    }
                }
                """,
                variables={"productId": self.product_bin.id},
            )
        # THEN
        self.assertEqual(res["cartAddItem"]["order"]["id"], self.sale_1.id)
        self.assertEqual(self.sale_1.state, "draft")
        sale_line_1 = self.sale_1.order_line
        self.assertEqual(len(sale_line_1), 1)
        self.assertEqual(sale_line_1.product_id, self.product_bin)
        self.assertEqual(sale_line_1.product_uom_qty, 10)
        # GIVEN
        # Check if we can still query product on cart if it was
        # unpublished after it was already in a cart.
        self.product_bin.is_published = False
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getProductFromCart {
                    cart {
                        order {
                            orderLines {
                                product {
                                    name
                                }
                            }
                        }
                    }
                }
                """,
            )
            self.assertEqual(
                res["cart"]["order"]["orderLines"], [{"product": {"name": "Pedal Bin"}}]
            )
