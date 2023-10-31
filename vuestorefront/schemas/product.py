# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import graphene
from graphql import GraphQLError
from odoo.http import request
from odoo import _

from odoo.addons.vuestorefront.schemas.objects import (
    SortEnum, Product, Attribute, AttributeValue
)


def get_search_order(sort):
    sorting = ''
    for field, val in sort.items():
        if sorting:
            sorting += ', '
        if field == 'price':
            sorting += 'list_price %s' % val.value
        else:
            sorting += '%s %s' % (field, val.value)

    # Add id as last factor so we can consistently get the same results
    if sorting:
        sorting += ', id ASC'
    else:
        sorting = 'id ASC'

    return sorting


def get_product_list(env, current_page, page_size, search, sort, **kwargs):
    Product = env['product.template'].sudo()
    domain = Product.prepare_vsf_domain(search, **kwargs)

    # First offset is 0 but first page is 1
    if current_page > 1:
        offset = (current_page - 1) * page_size
    else:
        offset = 0
    order = get_search_order(sort)
    products = Product.search(domain, order=order, offset=offset, limit=page_size)
    # Total count from the whole query is needed for creating proper pagination for it
    total_count = Product.search_count(domain)
    ProductAttributeValue = env['product.attribute.value']
    # TODO: either return standard attribute value from products or
    # redesign to not return anything instead of empty recordset (
    # ProductAttributeValue).
    # TODO: return some product prices instead of `0.0`.
    return products, total_count, ProductAttributeValue, 0.0, 0.0


class Products(graphene.Interface):
    products = graphene.List(Product)
    total_count = graphene.Int(required=True)
    attribute_values = graphene.List(AttributeValue)
    min_price = graphene.Float()
    max_price = graphene.Float()


class ProductList(graphene.ObjectType):
    class Meta:
        interfaces = (Products,)


class ProductFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    barcode = graphene.String()
    category_id = graphene.List(graphene.Int)
    category_slug = graphene.String()
    # Deprecated
    attribute_value_id = graphene.List(graphene.Int)
    attrib_values = graphene.List(graphene.String)
    name = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()


class ProductSortInput(graphene.InputObjectType):
    id = SortEnum()
    name = SortEnum()
    price = SortEnum()


class ProductVariant(graphene.Interface):
    product = graphene.Field(Product)
    product_template_id = graphene.Int()
    display_name = graphene.String()
    display_image = graphene.Boolean()
    price = graphene.Float()
    list_price = graphene.String()
    has_discounted_price = graphene.Boolean()
    is_combination_possible = graphene.Boolean()


class ProductVariantData(graphene.ObjectType):
    class Meta:
        interfaces = (ProductVariant,)


class ProductQuery(graphene.ObjectType):
    product = graphene.Field(
        Product,
        id=graphene.Int(default_value=None),
        slug=graphene.String(default_value=None),
        barcode=graphene.String(default_value=None),
    )
    products = graphene.Field(
        Products,
        filter=graphene.Argument(ProductFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(ProductSortInput, default_value={})
    )
    attribute = graphene.Field(
        Attribute,
        required=True,
        id=graphene.Int(),
    )
    product_variant = graphene.Field(
        ProductVariant,
        required=True,
        product_template_id=graphene.Int(),
        combination_id=graphene.List(graphene.Int)
    )

    @staticmethod
    def resolve_product(self, info, id=None, slug=None, barcode=None):
        env = info.context["env"]
        Product = product = env["product.template"].sudo()
        domain = None
        base_domain = [('is_published', '=', True)]
        if id:
            domain = base_domain + [('id', '=', id)]
        elif slug:
            domain = base_domain + [('website_slug', '=', slug)]
        elif barcode:
            domain = base_domain + [('barcode', '=', barcode)]
        if domain is not None:
            product = Product.search(domain, limit=1)
        if product:
            website = env['website'].get_current_website()
            request.website = website
            if not product.can_access_from_current_website():
                product = Product
        return product

    @staticmethod
    def resolve_products(self, info, filter, current_page, page_size, search, sort):
        env = info.context["env"]
        products, total_count, attribute_values, min_price, max_price = get_product_list(
            env, current_page, page_size, search, sort, **filter)
        return ProductList(products=products, total_count=total_count, attribute_values=attribute_values,
                           min_price=min_price, max_price=max_price)

    @staticmethod
    def resolve_attribute(self, info, id):
        return info.context["env"]["product.attribute"].search([('id', '=', id)], limit=1)

    @staticmethod
    def resolve_product_variant(self, info, product_template_id, combination_id):
        env = info.context["env"]

        website = env['website'].get_current_website()
        request.website = website
        pricelist = website.get_current_pricelist()

        product_template = env['product.template'].browse(product_template_id)
        combination = env['product.template.attribute.value'].browse(combination_id)

        variant_info = product_template._get_combination_info(combination, pricelist)

        product = env['product.product'].browse(variant_info['product_id'])

        # Condition to verify if Product exist
        if not product:
            raise GraphQLError(_('Product does not exist'))

        is_combination_possible = product_template._is_combination_possible(combination)

        # Condition to Verify if Product is active or if combination exist
        if not product.active or not is_combination_possible:
            variant_info['is_combination_possible'] = False
        else:
            variant_info['is_combination_possible'] = True

        return ProductVariantData(
            product=product,
            product_template_id=variant_info['product_template_id'],
            display_name=variant_info['display_name'],
            display_image=variant_info['display_image'],
            price=variant_info['price'],
            list_price=variant_info['list_price'],
            has_discounted_price=variant_info['has_discounted_price'],
            is_combination_possible=variant_info['is_combination_possible']
        )
