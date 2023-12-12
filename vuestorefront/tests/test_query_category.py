from . import common


class TestQueryCategory(common.TestVuestorefrontCommon):
    def test_01_query_categories(self):
        # WHEN
        res = self.execute(
            """
            query getCategory($ids: [Int]) {
                categories(filter: {ids: $ids}) {
                    categories {
                        name
                    }
                }
            }
            """,
            variables={"ids": self.public_category_bins.ids},
        )
        # THEN
        self.assertEqual(res["categories"]["categories"], [{"name": "Bins"}])
