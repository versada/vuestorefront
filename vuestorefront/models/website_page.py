import lxml

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
        # TODO: make it possible to render page without its layout
        # directly, so we would not need to strip rendered content
        # afterwards.
        content = self.env["ir.ui.view"]._render_template(
            self.view_id.id,
            {
                'deletable': True,
                'main_object': self,
                'website': website,
            }
        ).decode()
        content = self._postprocess_vsf_page_rendering(content, **kw)
        return content

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
