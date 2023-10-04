from graphene.test import Client

from odoo.tests.common import SavepointCase

from ..schema import schema


class TestVuestorefrontCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.graphene_client = Client(schema)
        cls.InvalidateCache = cls.env['invalidate.cache']
        cls.public_category_desks = cls.env.ref('website_sale.public_category_desks')
        cls.public_category_components = cls.env.ref(
            'website_sale.public_category_desks_components'
        )
        cls.public_category_bins = cls.env.ref('website_sale.public_category_bins')
        cls.product_tmpl_bin = cls.env.ref('product.product_product_9_product_template')

    def execute(self, query, **kw):
        res = self.graphene_client.execute(query, context={"env": self.env}, **kw)
        if not res:
            raise RuntimeError("GraphQL query returned no data")
        if res.get("errors"):
            raise RuntimeError(
                "GraphQL query returned error: {}".format(repr(res["errors"]))
            )
        return res.get("data")
