from . import common


class TestPublicCategory(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.InvalidateCache = cls.env['invalidate.cache']
        cls.public_category_desks = cls.env.ref('website_sale.public_category_desks')
        cls.public_category_components = cls.env.ref(
            'website_sale.public_category_desks_components'
        )
        cls.public_category_bins = cls.env.ref('website_sale.public_category_bins')
        cls.product_tmpl_bin = cls.env.ref('product.product_product_9_product_template')
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
