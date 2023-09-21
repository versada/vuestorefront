from odoo import models
from odoo.addons.http_routing.models.ir_http import slug


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_json_ld(self):
        self.ensure_one()
        if self.json_ld:
            return self.json_ld

        env = self.env
        website = env['website'].get_current_website()
        # TODO: reduce boilerplate
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            base_url = base_url.rstrip('/')

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
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": (
                        website
                        and website.display_name
                        or self.env.user.company_id.display_name
                    )
                }
            }
        }

        if self.description_sale:
            json_ld.update({"description": self.description_sale})

        if self.default_code:
            json_ld.update({"sku": self.default_code})

        return json_ld
