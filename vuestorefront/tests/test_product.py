
from . import common
from ..schemas.product import get_product_list


class TestProduct(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tmpl_bin = cls.env.ref('product.product_product_9_product_template')

    def test_01_get_product_list_by_name(self):
        res = get_product_list(
            self.env, 1, 100, "", {}, name=self.product_tmpl_bin.name
        )
        self.assertEqual(res[0], self.product_tmpl_bin)

    def test_02_product_slug(self):
        # GIVEN
        pt = self.product_tmpl_bin
        # WHEN
        pt.name = 'My product'
        self.assertEqual(pt.website_slug, f"my-product-{pt.id}")
