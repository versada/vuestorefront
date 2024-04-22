# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import graphene
from graphql import GraphQLError
from odoo.http import request
from odoo import _

from odoo.addons.vuestorefront.schemas.objects import (
    SortEnum, OrderStage, InvoiceStatus, Order, ShippingMethod,
    get_document_with_check_access,
    get_document_count_with_check_access
)

from ..utils import get_offset


def get_search_order(sort):
    sorting = ''
    for field, val in sort.items():
        if sorting:
            sorting += ', '
        sorting += '%s %s' % (field, val.value)

    # Add id as last factor so we can consistently get the same results
    if sorting:
        sorting += ', id ASC'
    else:
        sorting = 'id ASC'

    return sorting


class OrderFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    name = graphene.String()
    partner_name = graphene.String()
    stages = graphene.List(OrderStage)
    # Assuming YYYY-MM-DD format.
    date_from = graphene.String()
    date_to = graphene.String()
    invoice_status = graphene.List(InvoiceStatus)
    line_name = graphene.String()


class OrderSortInput(graphene.InputObjectType):
    id = SortEnum()
    date_order = SortEnum()
    name = SortEnum()
    state = SortEnum()


class UpdateOrderInput(graphene.InputObjectType):
    client_order_ref = graphene.String()


class Orders(graphene.Interface):
    orders = graphene.List(Order)
    total_count = graphene.Int(required=True)


class OrderList(graphene.ObjectType):
    class Meta:
        interfaces = (Orders,)


class OrderQuery(graphene.ObjectType):
    order = graphene.Field(
        Order,
        required=True,
        id=graphene.Int(),
        access_token=graphene.String(default_value=None)
    )
    orders = graphene.Field(
        Orders,
        filter=graphene.Argument(OrderFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=10),
        sort=graphene.Argument(OrderSortInput, default_value={})
    )
    delivery_methods = graphene.List(
        graphene.NonNull(ShippingMethod)
    )

    @staticmethod
    def resolve_order(self, info, id, access_token):
        SaleOrder = info.context['env']['sale.order']
        error_msg = 'Sale Order does not exist.'
        # This Condition will be used just on the Payment of one specific Order (
        # Public Access)
        if access_token:
            order = SaleOrder.sudo().search([('id', '=', id)], limit=1)
            if not order:
                raise GraphQLError(_(error_msg))
            if access_token != order.access_token:
                raise GraphQLError(_("Sorry! You cannot access this Order."))
        else:
            order = get_document_with_check_access(
                SaleOrder, [('id', '=', id)], error_msg=error_msg
            )
            if not order:
                raise GraphQLError(_(error_msg))
        return order.sudo()

    @staticmethod
    def resolve_orders(self, info, filter, current_page, page_size, sort):
        env = info.context["env"]
        partner = env.user.partner_id
        sort_order = get_search_order(sort)
        offset = get_offset(current_page, page_size)
        SaleOrder = env["sale.order"]
        domain = SaleOrder.prepare_vsf_domain(
            partner.commercial_partner_id.id, **filter
        )
        orders = get_document_with_check_access(
            SaleOrder,
            domain,
            sort_order,
            page_size,
            offset,
            error_msg='Sale Order does not exist.'
        )
        total_count = get_document_count_with_check_access(SaleOrder, domain)
        return OrderList(
            orders=orders and orders.sudo() or orders, total_count=total_count
        )

    @staticmethod
    def resolve_delivery_methods(self, info):
        """ Get all shipping/delivery methods """
        env = info.context['env']
        website = env['website'].get_current_website()
        request.website = website
        order = website.sale_get_order()
        return order._get_delivery_methods()


class UpdateOrder(graphene.Mutation):
    class Arguments:
        data = UpdateOrderInput(required=True)

    Output = Order

    @staticmethod
    def mutate(self, info, data):
        env = info.context["env"]
        website = env['website'].get_current_website()
        request.website = website
        order = website.sale_get_order(force_create=True)
        vals = order.prepare_vsf_vals(data)
        if vals:
            order.write(vals)
        return order


class ApplyCoupon(graphene.Mutation):
    class Arguments:
        promo = graphene.String()

    error = graphene.String()

    @staticmethod
    def mutate(self, info, promo):
        env = info.context["env"]
        website = env['website'].get_current_website()
        request.website = website
        order = website.sale_get_order(force_create=1)

        coupon_status = env['sale.coupon.apply.code'].sudo().apply_coupon(order, promo)

        return ApplyCoupon(error=coupon_status.get('not_found') or coupon_status.get('error'))


class OrderMutation(graphene.ObjectType):
    update_order = UpdateOrder.Field(description="Update Order")
    apply_coupon = ApplyCoupon.Field(description="Apply Coupon")
