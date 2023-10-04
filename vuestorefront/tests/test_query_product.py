from . import common


class TestQueryProduct(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.public_category_bins.website_slug = "bins"
        # Parent
        cls.public_category_desks.website_slug = "desks"
        # Child
        cls.public_category_components.website_slug = "components"

    def test_01_query_product_with_category_slug_single(self):
        # WHEN
        res = self.execute(
            """
            query getProductTemplates($ids: [Int], $categorySlug: String) {
                products(filter: {ids: $ids, categorySlug: $categorySlug}) {
                    products {
                        name
                    }
                }
            }
            """,
            variables={"ids": self.product_tmpl_bin.ids, "categorySlug": "bins"},
        )
        # THEN
        self.assertEqual(res["products"]["products"], [{"name": "Pedal Bin"}])

    def test_02_query_product_with_category_slug_is_child(self):
        # GIVEN
        self.product_tmpl_bin.public_categ_ids |= self.public_category_components
        # WHEN
        res = self.execute(
            """
            query getProductTemplates($ids: [Int], $categorySlug: String) {
                products(filter: {ids: $ids, categorySlug: $categorySlug}) {
                    products {
                        name
                    }
                }
            }
            """,
            # Related with child, calling from parent.
            variables={"ids": self.product_tmpl_bin.ids, "categorySlug": "desks"},
        )
        # THEN
        self.assertEqual(res["products"]["products"], [{"name": "Pedal Bin"}])

    def test_03_query_product_with_category_slug_is_parent(self):
        # GIVEN
        self.product_tmpl_bin.public_categ_ids |= self.public_category_desks
        # WHEN
        res = self.execute(
            """
            query getProductTemplates($ids: [Int], $categorySlug: String) {
                products(filter: {ids: $ids, categorySlug: $categorySlug}) {
                    products {
                        name
                    }
                }
            }
            """,
            # Related with parent, calling from child.
            variables={"ids": self.product_tmpl_bin.ids, "categorySlug": "components"},
        )
        # THEN
        self.assertEqual(res["products"]["products"], [])
