from graphene.test import Client

from odoo.tests.common import SavepointCase

from ..schema import schema


class TestVuestorefrontCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Website = cls.env["website"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ResUsers = cls.env['res.users']
        cls.ResPartner = cls.env["res.partner"]
        cls.PaymentTransaction = cls.env['payment.transaction']
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.graphene_client = Client(schema)
        cls.InvalidateCache = cls.env['invalidate.cache']
        cls.user_portal = cls.env.ref("base.demo_user0")
        cls.partner_portal = cls.user_portal.partner_id
        cls.public_category_desks = cls.env.ref('website_sale.public_category_desks')
        cls.public_category_components = cls.env.ref(
            'website_sale.public_category_desks_components'
        )
        cls.public_category_bins = cls.env.ref('website_sale.public_category_bins')
        cls.product_bin = cls.env.ref("product.product_product_9")
        cls.product_tmpl_bin = cls.product_bin.product_tmpl_id
        cls.country_lt = cls.env.ref("base.lt")
        cls.website_1 = cls.env.ref("website.default_website")
        cls.payment_acquirer_transfer = cls.env.ref(
            'payment.payment_acquirer_transfer'
        )
        cls.product_tmpl_bin.is_published = True

    def execute(self, query, **kw):
        res = self.graphene_client.execute(query, context={"env": self.env}, **kw)
        if not res:
            raise RuntimeError("GraphQL query returned no data")
        if res.get("errors"):
            raise RuntimeError(
                "GraphQL query returned error: {}".format(repr(res["errors"]))
            )
        return res.get("data")


class TestVuestorefrontSaleCommon(TestVuestorefrontCommon):
    """Common class to have patched active sale order for portal user."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (
            cls.partner_invoice_1,
            cls.partner_delivery_1,
            cls.partner_other_1,
        ) = cls.ResPartner.create(
            [
                {
                    "name": "Partner Invoice Address",
                    "street": "invoice 1",
                    "type": "invoice",
                    "parent_id": cls.partner_portal.id,
                },
                {
                    "name": "Partner Delivery Address",
                    "street": "delivery 1",
                    "type": "delivery",
                    "parent_id": cls.partner_portal.id,
                },
                {
                    "name": "Partner Other Address",
                    "street": "other 1",
                    "type": "other",
                    "parent_id": cls.partner_portal.id,
                },
            ]
        )

        cls.sale_1 = cls.SaleOrder.create(
            {
                "partner_id": cls.partner_portal.id,
                "partner_invoice_id": cls.partner_invoice_1.id,
                "partner_shipping_id": cls.partner_delivery_1.id,
            }
        )
        cls.sale_1_line_1 = cls.SaleOrderLine.create({
            "product_id": cls.product_bin.id,
            "product_uom_qty": 10,
            "order_id": cls.sale_1.id,
        })
        cls.Website._patch_method(
            "sale_get_order",
            lambda *args, **kw: cls.sale_1.with_user(cls.user_portal).sudo()
        )
        # To give access to portal user.
        cls.sale_1.message_subscribe(partner_ids=[cls.partner_portal.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.Website._revert_method("sale_get_order")
