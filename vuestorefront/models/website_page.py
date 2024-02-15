import lxml
import requests
from urllib.parse import urljoin

from odoo import models, api

from ..utils import get_website


class WebsitePage(models.Model):
    _inherit = 'website.page'

    @api.model
    def prepare_vsf_domain(self, **kw):
        website = get_website(self.env)
        website_id = website.sudo().id
        domain = [("website_id", "in", (False, website_id))]
        if kw.get('ids'):
            domain.append(("id", "in", kw["ids"]))
        if kw.get("name"):
            domain.append(("name", "=", kw["name"]))
        if kw.get("url"):
            domain.append(("url", "=", kw["url"]))
        return domain

    def render_vsf_page(self, **kw):
        self.ensure_one()
        website = get_website(self.env)
        # NOTE. Even if page has no website set, we assume current
        # website all the time for now.
        base_url = website.get_base_url()
        endpoint = urljoin(base_url, self.url)
        # TODO: make it possible to render page without its layout
        # directly, so we would not need to strip rendered content
        # afterwards.
        res = requests.get(endpoint)
        return self._postprocess_vsf_page_rendering(res.text, **kw)

    def _postprocess_vsf_page_rendering(self, content, **kw):
        self.ensure_one()
        excluded_tags = kw.get('excluded_tags')
        if excluded_tags:
            html_doc = lxml.html.fromstring(content)
            for tag in excluded_tags:
                elements = html_doc.iterfind(f".//{tag}")
                for element in elements:
                    element.getparent().remove(element)
            content = lxml.etree.tostring(html_doc, encoding="unicode", method="html")
        return content
