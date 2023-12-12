from unittest.mock import MagicMock, patch

from ..schemas import address
from . import common


@patch.object(address, "request", MagicMock())
class TestQueryMutateAddress(common.TestVuestorefrontSaleCommon):
    def test_01_query_addresses_delivery(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getAddresses($addressTypes: [AddressEnum]) {
                    addresses(filter: {addressTypes: $addressTypes}) {
                        name
                        street
                    }
                }
                """,
                variables={"addressTypes": ["Shipping"]},
            )
        # THEN
        self.assertEqual(
            sorted(res["addresses"], key=lambda x: x["name"]),
            sorted(
                [
                    {
                        "name": "Partner Delivery Address",
                        "street": "delivery 1",
                    },
                ],
                key=lambda x: x["name"],
            ),
        )

    def test_02_query_addresses_invoice_n_delivery(self):
        # GIVEN
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                query getAddresses($addressTypes: [AddressEnum]) {
                    addresses(filter: {addressTypes: $addressTypes}) {
                        name
                        street
                    }
                }
                """,
                variables={"addressTypes": ["Billing", "Shipping"]},
            )
        # THEN
        self.assertEqual(
            sorted(res["addresses"], key=lambda x: x["name"]),
            sorted(
                [
                    {
                        "name": "Partner Invoice Address",
                        "street": "invoice 1",
                    },
                    {
                        "name": "Partner Delivery Address",
                        "street": "delivery 1",
                    },
                ],
                key=lambda x: x["name"],
            ),
        )

    def test_03_mutate_create_delivery_address(self):
        # GIVEN
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation AddAddress($addressType: AddressEnum!, $countryId: Int!) {
                    addAddress (
                        addressType: $addressType,
                        address: {
                            name: "Partner Delivery Address 2"
                            street: "delivery 2"
                            zip: "zip 2"
                            countryId: $countryId
                            phone: "123456"
                        }
                    ) {
                        id
                    }
                }
                """,
                variables={"addressType": "Shipping", "countryId": self.country_lt.id},
            )
        # THEN
        partner = self.ResPartner.browse(res["addAddress"]["id"])
        self.assertEqual(partner.street, "delivery 2")
        self.assertEqual(self.sale_1.partner_shipping_id, partner)

    def test_04_mutate_update_delivery_address(self):
        # GIVEN
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation UpdateAddress($id: Int!) {
                    updateAddress (
                        address: {
                            id: $id
                            street: "delivery 1 updated"
                        }
                    ) {
                        id
                    }
                }
                """,
                variables={"id": self.partner_delivery_1.id},
            )
        # THEN
        partner = self.ResPartner.browse(res["updateAddress"]["id"])
        self.assertEqual(partner, self.partner_delivery_1)
        self.assertEqual(partner.street, "delivery 1 updated")
