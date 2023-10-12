from odoo import models, fields, api


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    website_slug = fields.Char('Website Slug', copy=False, index=True)
    json_ld = fields.Char('JSON-LD')

    _sql_constraints = [
        (
            'website_slug_uniq',
            'unique (website_slug)',
            'The Website Slug must be unique!',
        )
    ]

    def write(self, vals):
        res = super(ProductPublicCategory, self).write(vals)
        self.env['invalidate.cache'].create_invalidate_cache(self._name, self.ids)
        return res

    def unlink(self):
        self.env['invalidate.cache'].create_invalidate_cache(self._name, self.ids)
        return super(ProductPublicCategory, self).unlink()

    def get_json_ld(self):
        self.ensure_one()
        if self.json_ld:
            return self.json_ld

        website = self.env['website'].get_current_website()
        base_url = website.domain
        if base_url:
            base_url = base_url.rstrip('/')

        json_ld = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "url": '{}{}'.format(base_url, self.website_slug or ''),
            "name": self.display_name,
        }

        return json_ld

    def get_ancestors(self):
        for categ in self:
            parent = categ.parent_id
            while parent:
                yield parent
                parent = parent.parent_id

    @api.model
    def _get_category_slug_leaf(self, category_slug):
        # We need to search for category, because we want to include child
        # categories.
        categ = self.env['product.public.category'].search(
            [('website_slug', '=', category_slug)]
        )
        if categ:
            return ('public_categ_ids', 'child_of', categ.id)
        return None
