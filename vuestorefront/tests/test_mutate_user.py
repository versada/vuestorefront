from unittest.mock import MagicMock, patch

from ..schemas import sign
from . import common


class TestMutateUser(common.TestVuestorefrontCommon):
    @patch.object(sign, "request", MagicMock())
    def test_01_register_new_user(self):
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation Register(
                    $name: String!, $email: String!, $password: String!
                ) {
                    register (
                        name: $name
                        email: $email
                        password: $password
                        extra: {vat: "XX123"}
                    ) {
                        id
                    }
                }
                """,
                variables={
                    "name": "my-name-1",
                    "email": "my-login-1",
                    "password": "my-password",  # pragma: allowlist secret
                },
            )
        # THEN
        user = self.ResUsers.browse(res["register"]["id"])
        self.assertEqual(user.login, "my-login-1")
        self.assertEqual(user.partner_id.vat, "XX123")
