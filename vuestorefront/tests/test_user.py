from unittest.mock import patch

from odoo.tests.common import new_test_user

from ..models.website import Website as Website
from .common import TestVuestorefrontSaleCommon

PATH_PATCH_USER_REQ = "odoo.addons.vuestorefront.models.res_users.request"


get_vsf_http_domain_origin = Website.get_vsf_http_domain


def get_vsf_http_domain_patched(self):
    return get_vsf_http_domain_origin(self)


class TestUser(TestVuestorefrontSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test_one = new_test_user(
            cls.env,
            login='user_test_one_123',
            name='Test User',
            company_id=cls.company_main.id,
            company_ids=[(6, 0, cls.company_main.ids)],
        )

    @patch(PATH_PATCH_USER_REQ)
    @patch.object(
        Website,
        'get_vsf_http_domain',
        autospec=True,
        wraps=Website,
        side_effect=get_vsf_http_domain_patched,
    )
    def test_01_test_reset_user_password_ok(self, m1, req1):
        # GIVEN
        req1.env = self.env
        # WHEN
        self.user_test_one.api_action_reset_password()
        # THEN
        self.assertTrue(m1.called)
        # Imitate same call for get_vsf_http_domain_origin to see if
        # correct domain was returned.
        self.assertEqual(m1(self.website_1), 'http://example.com')
