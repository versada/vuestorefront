import json

from odoo import api, fields, models

from ..utils import slugify_with_sfx


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    slug = fields.Char(
        readonly=False,
        index=True,
        store=True,
        compute="_compute_slug",
    )
    json_ld = fields.Char("JSON-LD")

    _sql_constraints = [
        (
            "slug_uniq",
            "unique (slug)",
            "The Website Slug must be unique!",
        )
    ]

    @api.depends("name")
    def _compute_slug(self):
        for rec in self:
            if not isinstance(rec.id, models.NewId) and not rec.slug and rec.name:
                rec.slug = slugify_with_sfx(rec.name, f"-{rec.id}")

    def write(self, vals):
        res = super().write(vals)
        self.env["invalidate.cache"].create_invalidate_cache(self._name, self.ids)
        return res

    def unlink(self):
        self.env["invalidate.cache"].create_invalidate_cache(self._name, self.ids)
        return super().unlink()

    def get_json_ld(self):
        self.ensure_one()
        if self.json_ld:
            return self.json_ld

        website = self.env["website"].get_current_website()
        base_url = website.domain or ""
        if base_url and base_url[-1] == "/":
            base_url = base_url[:-1]

        json_ld = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "url": "{}{}".format(base_url, self.slug or ""),
            "name": self.display_name,
        }

        return json.dumps(json_ld)

    def get_ancestors(self):
        for categ in self:
            parent = categ.parent_id
            while parent:
                yield parent
                parent = parent.parent_id

    def get_category_by_slug(self, slug):
        return self.search([("slug", "=", slug)])

    @api.model
    def _get_category_slug_leaf(self, category_slug):
        # We need to search for category, because we want to include child
        # categories.
        categ = self.get_category_by_slug(category_slug)
        if categ:
            return ("public_categ_ids", "child_of", categ.id)
        return None
