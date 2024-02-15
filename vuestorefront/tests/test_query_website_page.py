from unittest.mock import patch

from odoo.tests.common import HttpCaseCommon, get_db_name

from . import common

PATH_UTILS_REQ = "odoo.addons.vuestorefront.utils.request"
# TODO: we should redesign rendering to use it directly without external
# request call. Then we would need to use these paths, so keeping for now.
PATH_IR_UI_VIEW_REQ = "odoo.addons.base.models.ir_ui_view.request"
PATH_WEBSITE_REQ = "odoo.addons.website.models.website.request"
PATH_WEBSITE_IR_UI_VIEW_REQ = "odoo.addons.website.models.ir_ui_view.request"
PATH_WEBSITE_IR_HTTP_REQ = "odoo.addons.website.models.ir_http.request"
PATH_WEBSITE_RES_LANG_REQ = "odoo.addons.website.models.res_lang.request"
PATH_PORTAL_IR_UI_VIEW_REQ = "odoo.addons.portal.models.ir_ui_view.request"
PATH_HTTP_ROUTING_REQ = "odoo.addons.http_routing.models.ir_http.request"
PATH_WEB_IR_HTTP_REQ = "odoo.addons.web.models.ir_http.request"
PATH_WEBSITE_SALE_WEBSITE_REQ = "odoo.addons.website_sale.models.website.request"


def update_mocked_requests(self, path, *mocked_requests):
    website = self.website_1
    lang = self.lang_us
    env = self.env
    for req in mocked_requests:
        req.website = website
        req.lang = lang
        req.env = env
        req.is_frontend = True
        req.is_frontend_multilang = False
        req.editable = False
        req.translatable = False
        req.session.uid = self.user_portal.id
        req.session.get_context = lambda: {'lang': 'en_US', 'uid': req.session.uid}
        req.httprequest.path = path


def patch_get_frontend_session_info(cls):
    def patch_it(s):
        return {
            'is_admin': False,
            'is_system': False,
            'is_website_user': True,
            'user_id': cls.user_portal.id,
            'is_frontend': True,
            'lang_url_code': 'en_US',
        }
    return patch_it


class TestQueryWebsitePage(common.TestVuestorefrontCommon, HttpCaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lang_us = cls.env.ref("base.lang_en")
        cls.WebsiteSeoMetadata = cls.env['website.seo.metadata']
        cls.IrHttp = cls.env["ir.http"]
        cls.website_page_contactus = cls.env.ref("website.contactus_page")
        cls.view_recaptcha = cls.env.ref('google_recaptcha.assets_frontend')
        # Disable to make it easier to test.
        cls.view_recaptcha.active = False
        cls.WebsiteSeoMetadata._patch_method('get_website_meta', lambda s: {})

    @patch(PATH_UTILS_REQ)
    def test_01_query_website_page_with_content_exclude_some_tags(self, *mock_requests):
        # GIVEN
        self.url_open(f"/web?db={get_db_name()}", timeout=20)
        update_mocked_requests(self, self.website_page_contactus.url, *mock_requests)
        # WHEN
        res = self.execute(
            """
            query getWebsitePage(
                $id: Int, $contentRendering: WebsitePageContentInput)
            {
                websitePage(
                    id: $id,
                    contentRendering: $contentRendering
                ) {
                    websitePage {
                        name
                        url
                    }
                    content
                }
            }
            """,
            variables={
                "id": self.website_page_contactus.id,
                "contentRendering": {
                    "contentIncluded": True,
                    "excludedTags": ["header", "footer"]
                },
            },
        )
        # THEN
        self.assertEqual(
            res["websitePage"]["websitePage"],
            {
                "name": "Contact Us",
                "url": "/contactus",
            }
        )
        content = res["websitePage"]["content"]
        self.assertIn('</html>', content)
        self.assertNotIn('</header>', content)
        self.assertNotIn('</footer>', content)

    @patch(PATH_UTILS_REQ)
    def test_02_query_website_pages_no_content(self, req1):
        # WHEN
        res = self.execute(
            """
            query getWebsitePages($url: String) {
                websitePages(
                    filter: {url: $url}
                ) {
                    websitePages {
                        id
                        name
                        url
                    }
                    contents
                }
            }
            """,
            variables={"url": '/contactus'},
        )
        # THEN
        self.assertEqual(
            res["websitePages"]["websitePages"],
            [
                {
                    "id": self.website_page_contactus.id,
                    "name": "Contact Us",
                    "url": "/contactus",
                }
            ]
        )
        self.assertEqual(res["websitePages"]["contents"], [""])

    @patch(PATH_UTILS_REQ)
    def test_03_query_website_pages_with_content_all_tags(self, *mock_requests):
        # GIVEN
        update_mocked_requests(self, self.website_page_contactus.url, *mock_requests)
        # WHEN
        res = self.execute(
            """
            query getWebsitePages(
            $url: String, $contentRendering: WebsitePageContentInput
            ) {
                websitePages(
                    filter: {url: $url},
                    contentRendering: $contentRendering
                ) {
                    websitePages {
                        id
                        name
                        url
                    }
                    contents
                }
            }
            """,
            variables={
                "url": '/contactus',
                "contentRendering": {"contentIncluded": True},
            },
        )
        # THEN
        self.assertEqual(
            res["websitePages"]["websitePages"],
            [
                {
                    "id": self.website_page_contactus.id,
                    "name": "Contact Us",
                    "url": "/contactus",
                }
            ]
        )
        self.assertEqual(len(res["websitePages"]["contents"]), 1)
        content = res["websitePages"]["contents"][0]
        self.assertIn('</html>', content)
        self.assertIn('</header>', content)
        self.assertIn('</footer>', content)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.WebsiteSeoMetadata._revert_method('get_website_meta')
