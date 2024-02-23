import graphene
from graphql import GraphQLError

from ..utils import get_website, get_offset

from .objects import WebsitePage


class WebsitePagesI(graphene.Interface):
    website_pages = graphene.List(WebsitePage)
    total_count = graphene.Int(required=True)


class WebsitePageList(graphene.ObjectType):
    class Meta:
        interfaces = (WebsitePagesI,)


class WebsitePageContentInput(graphene.InputObjectType):
    excluded_tags = graphene.List(graphene.String)


class WebsitePageFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    name = graphene.String()
    url = graphene.String()


class WebsitePageQuery(graphene.ObjectType):
    website_page = graphene.Field(
        WebsitePage,
        required=True,
        id=graphene.Int(default_value=None),
        name=graphene.String(default_value=None),
        url=graphene.String(default_value=None),
        content_options=graphene.Argument(WebsitePageContentInput, default_value={})
    )
    website_pages = graphene.Field(
        WebsitePagesI,
        filter=graphene.Argument(WebsitePageFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        content_options=graphene.Argument(WebsitePageContentInput, default_value={}),
    )

    def resolve_website_page(
        self, info, id=None, name=None, url=None, content_options=None
    ):
        if content_options is None:
            content_options = {}
        env = info.context["env"]
        WebsitePage = env['website.page'].sudo()
        domain_kwargs = {"name": name, "url": url}
        if id:
            domain_kwargs["ids"] = [id]
        domain = WebsitePage.prepare_vsf_domain(**domain_kwargs)
        # TODO: we should not simply limit to 1 as its not correct. We
        # should raise exception if more than one record is found (though
        # limit=1 logic is now used all over the module, so keeping it
        # for consistency..)
        page = WebsitePage.search(domain, limit=1)
        website = get_website(env)
        if page.website_id and page.website_id != website:
            raise GraphQLError("Website page does not exist!")
        return page.with_context(website_page_content_options=content_options)

    @staticmethod
    def resolve_website_pages(
        self, info, filter, current_page, page_size, content_options
    ):
        env = info.context["env"]
        WebsitePage = env['website.page'].sudo()
        domain = WebsitePage.prepare_vsf_domain(**filter)
        offset = get_offset(current_page, page_size)
        website_pages = WebsitePage.search(domain, offset=offset, limit=page_size)
        total_count = WebsitePage.search_count(domain)
        return WebsitePageList(
            website_pages=website_pages.with_context(
                website_page_content_options=content_options
            ),
            total_count=total_count,
        )
