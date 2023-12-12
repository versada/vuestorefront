==============
Vue Storefront
==============

This is a forked module previously called ``graphql_vuestorefront``. It
is backwards incompatible module, so it should not be installed
alongside ``graphql_vuestorefront``. Custom changes different than in
forked module:

* ``get_product_list`` in ``schemas.product`` now uses offset/limit in standard
  search instead of searching for all possible products and then slicing (
  which has terrible performance).
* ``website_slug``: (renamed to ``slug``) got rid of translate awareness (
  to simplify it), and not adding
  slashes in slug, because slug is not supposed to have that. (on category, removed
  validation as it was forcing to use slash. Added unique constraint, because
  category slug can be entered manually).
* Split odoo model files into more appropriate, to make it more readable and
  maintainable.
* Removed ``public_categ_slug_ids`` field as it was confusing and redundant
  field that was very slow to compute for large amount of products.
* implemented ``products`` ``category_slug`` filter.
* moved Product schema domain method to ``product.template`` to be extendable.

Addresses
---------

* Moved address domain methods on ``res.partner`` to be extendable.
* Moved preparation of partner (address) creation/update on ``res.partner to
  be extendable.

Sale Order
----------

* Added UpdateOrder mutation to be able to update some data on sale order.

Users
-----

* Can pass extra data when signing up (only ``vat`` for now).

Login
=====

To authenticate, use the default /web/session/authenticate endpoint.
Example using axios:

.. code-block::

    axios.post('<domain>/web/session/authenticate', {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": <database_name>,
            "login": <user_login>,
            "password": <user_password>
    }}, {
        "withCredentials": true
    })

Logout
======

.. code-block::

    axios.post('<domain>/web/session/destroy', {
        "jsonrpc": "2.0",
        "method": "call"
    }, {
        "withCredentials": true
    })

Add to Cart
===========

.. code-block::

    axios.post('<domain>/shop/cart/update_json', {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_id": <product_id>,
            "add_qty": <qty>
    }}, {
        "withCredentials": true
    })

Add to wishlist
===============

.. code-block::

    axios.post('<domain>/shop/wishlist/add', {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_id": <product_id>,
    }}, {
        "withCredentials": true
    })

Remove from wishlist
====================

.. code-block::

    axios.post('<domain>/shop/wishlist/remove/<product_wishlist_id>', {
        "jsonrpc": "2.0",
        "method": "call"
    }, {
        "withCredentials": true
    })

Get the rate for a shipping method
==================================

.. code-block::

    axios.post('<domain>/shop/carrier_rate_shipment', {
        "jsonrpc": "2.0",
        "method": "call"
        "params": {
            "carrier_id": <ShippingMethod.ID>,
    }}, {
        "withCredentials": true
    })

Get all product template attributes for product template page
=============================================================

.. code-block::

    axios.post('<domain>/shop/get_combinations/<int:product_template_id>', {
        "jsonrpc": "2.0",
        "method": "call"
    }, {
        "withCredentials": true
    })

Get product id and price after selecting the combination on the product template page
=====================================================================================

.. code-block::

    axios.post('<domain>/shop/get_combination_info/<int:product_template_id>', {
        "jsonrpc": "2.0",
        "method": "call"
        "params": {
            "combination_ids": [1, 2],
            add_qty=1
    }}, {
        "withCredentials": true
    })

Get products for shop with search, category, sort, count, pagination and attributes filtering
=============================================================================================

.. code-block::

    axios.post('<domain>/shop/products', {
        "jsonrpc": "2.0",
        "method": "call"
        "params": {
            "search": "",
            "category_id": 1,
            "offset": 0,
            "ppg": 20,
            "attrib_list": []
    }}, {
        "withCredentials": true
    })
