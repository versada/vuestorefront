# -*- coding: utf-8 -*-
# Copyright 2021 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import graphene
from graphql import GraphQLError
from odoo import _

from odoo.addons.vuestorefront.schemas.objects import (
    SortEnum,
    Invoice,
    InvoiceState,
    InvoicePaymentState,
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


class InvoiceFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    name = graphene.String()
    states = graphene.List(InvoiceState)
    # Assuming YYYY-MM-DD format.
    date_from = graphene.String()
    date_to = graphene.String()
    payment_states = graphene.List(InvoicePaymentState)
    line_name = graphene.String()


class InvoiceSortInput(graphene.InputObjectType):
    id = SortEnum()
    invoice_date = SortEnum()
    name = SortEnum()
    state = SortEnum()


class Invoices(graphene.Interface):
    invoices = graphene.List(Invoice)
    total_count = graphene.Int(required=True)


class InvoiceList(graphene.ObjectType):
    class Meta:
        interfaces = (Invoices,)


class InvoiceQuery(graphene.ObjectType):
    invoice = graphene.Field(
        Invoice,
        required=True,
        id=graphene.Int(),
    )
    invoices = graphene.Field(
        Invoices,
        filter=graphene.Argument(InvoiceFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=10),
        sort=graphene.Argument(InvoiceSortInput, default_value={})
    )

    @staticmethod
    def resolve_invoice(self, info, id):
        AccountMove = info.context["env"]['account.move']
        error_msg = 'Invoice does not exist.'
        invoice = get_document_with_check_access(
            AccountMove, [('id', '=', id)], error_msg=error_msg
        )
        if not invoice:
            raise GraphQLError(_(error_msg))
        return invoice.sudo()

    @staticmethod
    def resolve_invoices(self, info, filter, current_page, page_size, sort):
        env = info.context["env"]
        AccountMove = env["account.move"]
        partner = env.user.partner_id
        sort_order = get_search_order(sort)
        domain = AccountMove.prepare_vsf_domain(
            partner.commercial_partner_id.id,
            **filter,
        )
        offset = get_offset(current_page, page_size)
        invoices = get_document_with_check_access(
            AccountMove,
            domain,
            sort_order,
            page_size,
            offset,
            error_msg='Invoice does not exist.'
        )
        total_count = get_document_count_with_check_access(AccountMove, domain)
        return InvoiceList(
            invoices=invoices and invoices.sudo() or invoices, total_count=total_count
        )
