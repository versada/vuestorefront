# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api
from odoo.tools.sql import column_exists, create_column

from odoo.addons.http_routing.models.ir_http import slug, slugify


def slugify_with_sfx(value, sfx):
    return f"{slugify(value)}{sfx}"


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _auto_init(self):
        """Create/set website_slug via SQL to save on memory usage."""
        cr = self.env.cr
        if not column_exists(
            cr, "product_template", "website_slug"
        ):
            create_column(
                cr, "product_template", "website_slug", "varchar"
            )
            cr.execute("SELECT id, name FROM product_template WHERE name IS NOT NULL")
            for res in cr.fetchall():
                id_, name = res
                cr.execute(
                    "UPDATE product_template SET website_slug = %s WHERE id = %s",
                    (slugify_with_sfx(name, f"-{id_}"), id_)
                )
        return super()._auto_init()

    website_slug = fields.Char(
        'Website Slug',
        compute='_compute_website_slug',
        store=True,
        readonly=True,
        index=True,
    )
    json_ld = fields.Char('JSON-LD')

    @api.depends('name')
    def _compute_website_slug(self):
        for product in self:
            # To make sure we don't assign ID before record is created.
            if not isinstance(product.id, models.NewId):
                product.website_slug = slugify_with_sfx(product.name, f"-{product.id}")

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self.env['invalidate.cache'].create_invalidate_cache(self._name, self.ids)
        return res

    def unlink(self):
        self.env['invalidate.cache'].create_invalidate_cache(self._name, self.ids)
        return super(ProductTemplate, self).unlink()

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False
    ):
        """Add discount value and percentage based."""
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        discount = 0
        discount_perc = 0

        if combination_info['has_discounted_price']:
            discount = combination_info['list_price'] - combination_info['price']
            discount_perc = combination_info['list_price'] and (
                discount * 100 / combination_info['list_price']
            ) or 0

        combination_info.update({
            'discount': round(discount, 2),
            'discount_perc': int(discount_perc),
        })

        return combination_info

    def get_json_ld(self):
        self.ensure_one()
        if self.json_ld:
            return self.json_ld

        env = self.env
        website = env['website'].get_current_website()
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        if base_url and base_url[-1:] == '/':
            base_url = base_url[:-1]

        # Get list of images
        images = list()
        if self.image_1920:
            images.append('%s/web/image/product.product/%s/image' % (base_url, self.id))

        json_ld = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": self.display_name,
            "image": images,
            "offers": {
                "@type": "Offer",
                "url": "%s/product/%s" % (website.domain or '', slug(self)),
                "priceCurrency": self.currency_id.name,
                "price": self.list_price,
                "itemCondition": "https://schema.org/NewCondition",
                # TODO: implement a way to show real stock?
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": website and website.display_name or self.env.user.company_id.display_name
                }
            }
        }

        if self.description_sale:
            json_ld.update({"description": self.description_sale})

        if self.default_code:
            json_ld.update({"sku": self.default_code})

        return json_ld
