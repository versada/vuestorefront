from unittest.mock import patch

from . import common

PATH_PATCH_SIGN_REQ = "odoo.addons.vuestorefront.schemas.sign.request"


class TestMutateUser(common.TestVuestorefrontCommon):
    @patch(PATH_PATCH_SIGN_REQ)
    def test_01_register_new_user(self, req1):
        # GIVEN
        req1.website = self.website_1
        # WHEN
        with self.with_user("portal"):
            res = self.execute(
                """
                mutation Register($name: String!, $email: String!, $password: String!) {
                    register (
                        name: $name
                        email: $email
                        password: $password
                    ) {
                        id
                    }
                }
                """,
                variables={
                    "name": "my-name-1",
                    "email": "my-login-1",
                    "password": "my-password",
                },
            )
        # THEN
        user = self.ResUsers.browse(res["register"]["id"])
        self.assertEqual(user.login, "my-login-1")
