import requests_mock

from . import common
from .. import const

VSF_CACHE_URL = "https://example.com"


class TestWebsitePageViewCache(common.TestVuestorefrontCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.website_page_contactus = cls.env.ref("website.contactus_page")
        cls.view_layout = cls.env.ref("website.layout")
        cls.IrConfigParameter.set_param(const.CFG_PARAM_VSF_CACHE_ENABLE, "True")
        cls.IrConfigParameter.set_param(const.CFG_PARAM_VSF_CACHE_URL, VSF_CACHE_URL)
        cls.IrConfigParameter.set_param(const.CFG_PARAM_VSF_CACHE_KEY, "abc123")

    @requests_mock.Mocker()
    def test_01_website_page_view_cache_invalidation_ok(self, m):
        # GIVEN
        adapter = m.get(VSF_CACHE_URL, status_code=200, text="OK")
        # WHEN
        self.website_page_contactus.view_id.priority = 17
        # THEN
        view_id = self.website_page_contactus.view_id.id
        self.assertEqual(adapter.call_count, 1)
        self.assertEqual(adapter.last_request.query, f"key=abc123&tags=iuv{view_id}")

    @requests_mock.Mocker()
    def test_02_website_page_view_cache_invalidation_non_page_view(self, m):
        # GIVEN
        adapter = m.get(VSF_CACHE_URL, status_code=200, text="OK")
        # WHEN
        self.view_layout.priority = 17
        # THEN
        self.assertEqual(adapter.call_count, 0)

    @requests_mock.Mocker()
    def test_03_website_page_view_cache_invalidation_disabled(self, m):
        # GIVEN
        self.IrConfigParameter.set_param(const.CFG_PARAM_VSF_CACHE_ENABLE, False)
        adapter = m.get(VSF_CACHE_URL, status_code=200, text="OK")
        # WHEN
        self.website_page_contactus.view_id.priority = 17
        # THEN
        self.assertEqual(adapter.call_count, 0)

    @requests_mock.Mocker()
    def test_04_website_page_view_cache_invalidation_manual(self, m):
        # GIVEN
        adapter = m.get(VSF_CACHE_URL, status_code=200, text="OK")
        # WHEN
        self.website_page_contactus.action_invalidate_vsf_cache()
        # THEN
        view_id = self.website_page_contactus.view_id.id
        self.assertEqual(adapter.call_count, 1)
        self.assertEqual(adapter.last_request.query, f"key=abc123&tags=iuv{view_id}")
