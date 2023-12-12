from ..schemas.product import get_product_list
from . import common


class TestProduct(common.TestVuestorefrontCommon):
    def test_01_get_product_list_by_name(self):
        # WHEN
        res = get_product_list(
            self.env, 1, 100, "", {}, name=self.product_tmpl_bin.name
        )
        # THEN
        self.assertEqual(res[0], self.product_tmpl_bin)

    def test_02_product_slug(self):
        # GIVEN
        pt = self.product_tmpl_bin
        # WHEN
        pt.name = "My product"
        # THEN
        self.assertEqual(pt.slug, f"my-product-{pt.id}")
