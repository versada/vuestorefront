from odoo import models

from ..utils import format_vsf_cache_tags, invalidate_vsf_cache
from .. import const

TAG_PFX = "iuv"


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def get_vsf_cache_tags(self):
        return format_vsf_cache_tags(TAG_PFX, self.ids)

    def write(self, vals):
        res = super().write(vals)
        self.invalidate_website_page_views_cache()
        return res

    def unlink(self):
        self.invalidate_website_page_views_cache()
        return super().unlink()

    def invalidate_website_page_views_cache(self):
        ICP = self.env['ir.config_parameter'].sudo()
        # TODO: for now we are checking URL/KEY instead of
        # CFG_PARAM_VSF_CACHE_ENABLE here, so we could use website page
        # cache when the rest of caching is disabled. Normally all
        # caching should be enabled.
        if (
            not ICP.get_param(const.CFG_PARAM_VSF_CACHE_URL)
            or not ICP.get_param(const.CFG_PARAM_VSF_CACHE_KEY)
        ):
            return False
        views = self._get_website_page_views()
        if views:
            invalidate_vsf_cache(
                self.env, views.get_vsf_cache_tags(),
                raise_err=False,
            )
            return True
        return False

    def _get_website_page_views(self):
        return self.filtered(lambda r: r.page_ids)
