from odoo.addons.http_routing.models.ir_http import slugify


def slugify_with_sfx(value, sfx):
    return f"{slugify(value)}{sfx}"


def get_offset(current_page, page_size):
    # First offset is 0 but first page is 1
    if current_page > 1:
        return (current_page - 1) * page_size
    return 0
