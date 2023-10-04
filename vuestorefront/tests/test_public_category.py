from . import common


class TestPublicCategory(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tmpl_bin.public_categ_ids |= cls.public_category_components

    def test_01_get_product_tags(self):
        # WHEN
        res = self.InvalidateCache._get_product_tags(self.product_tmpl_bin.ids)
        # THEN
        res = res.split(",")
        self.assertEqual(len(res), 4)
        self.assertIn(f"P{self.product_tmpl_bin.id}", res)
        self.assertIn(f"C{self.public_category_bins.id}", res)
        self.assertIn(f"C{self.public_category_components.id}", res)
        self.assertIn(f"C{self.public_category_desks.id}", res)
