from unittest.mock import patch

from .common import TestVuestorefrontSaleCommon

PATH_PATCH_SHOP_REQ = "odoo.addons.vuestorefront.schemas.shop.request"


class TestMutateShop(TestVuestorefrontSaleCommon):
    @patch(PATH_PATCH_SHOP_REQ)
    def test_01_mutate_add_to_cart(self, req1):
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
                variables={"productId": self.product_bin.id}
            )
        # THEN
        self.assertEqual(res["cartAddItem"]["order"]["id"], self.sale_1.id)
        self.assertEqual(self.sale_1.state, "draft")
        sale_line_1 = self.sale_1.order_line
        self.assertEqual(len(sale_line_1), 1)
        self.assertEqual(sale_line_1.product_id, self.product_bin)
        self.assertEqual(sale_line_1.product_uom_qty, 10)
