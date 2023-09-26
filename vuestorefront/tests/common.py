from graphene.test import Client

from odoo.tests.common import SavepointCase

from ..schema import schema


class TestVuestorefrontCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.graphene_client = Client(schema)

    def execute(self, query, **kw):
        res = self.graphene_client.execute(query, context={"env": self.env}, **kw)
        if not res:
            raise RuntimeError("GraphQL query returned no data")
        if res.get("errors"):
            raise RuntimeError(
                "GraphQL query returned error: {}".format(repr(res["errors"]))
            )
        return res.get("data")
