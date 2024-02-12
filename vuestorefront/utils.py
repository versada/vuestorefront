from odoo.http import request


def get_offset(current_page, page_size):
    # First offset is 0 but first page is 1
    if current_page > 1:
        return (current_page - 1) * page_size
    return 0


def to_camel_case(snake_str):
    return "".join(s.capitalize() for s in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str):
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def get_image_endpoint(model, res_id, fname):
    return f"/web/image/{model}/{res_id}/{fname}"


def get_website(env):
    website = env['website'].get_current_website()
    request.website = website
    return website
