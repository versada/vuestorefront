from datetime import datetime
import requests
import logging

from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from . import const

_logger = logging.getLogger(__name__)


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


def format_vsf_cache_tags(pfx, ids):
    ids_str = ",".join((str(id_)) for id_ in ids)
    return f"{pfx}{ids_str}"


def date_string_to_datetime(dt_str, hour=0, minute=0, second=0):
    dt = datetime.strptime(dt_str, DEFAULT_SERVER_DATE_FORMAT)
    return dt.replace(hour=hour, minute=minute, second=second)


# TODO: invalidate.cache should be redesigned to be generic enough to
# handle cache invalidation for all kinds of models (merging this function with
# that). Now it is implemented with only specific models in mind.
def invalidate_vsf_cache(env, tags, raise_err=False):
    ICP = env["ir.config_parameter"].sudo()
    # If this function is called, we assume parameters are set.
    url = ICP.get_param(const.CFG_PARAM_VSF_CACHE_URL)
    key = ICP.get_param(const.CFG_PARAM_VSF_CACHE_KEY)
    try:
        res = requests.get(
            url, params={'key': key, 'tags': tags}, timeout=const.VSF_VACHE_TIMEOUT
        )
        if not res.ok:
            _logger.warning("Cache invalidation failed. Error: %s", res.text)
            return False
    except Exception as e:
        if raise_err:
            raise
        _logger.error(
            "Something went wrong invalidating VSF cache. Error: %s", e
        )
    return True
