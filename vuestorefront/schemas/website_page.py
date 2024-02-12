import graphene
from graphql import GraphQLError

from ..utils import get_website, get_offset

from .objects import WebsitePage


class WebsitePageI(graphene.Interface):
    website_page = graphene.Field(lambda: WebsitePage)
    content = graphene.String()


class WebsitePagesI(graphene.Interface):
    website_pages = graphene.List(WebsitePage)
    total_count = graphene.Int(required=True)
    contents = graphene.List(graphene.NonNull(graphene.String))


class WebsitePageWithContent(graphene.ObjectType):
    class Meta:
        interfaces = (WebsitePageI,)


class WebsitePageList(graphene.ObjectType):
    class Meta:
        interfaces = (WebsitePagesI,)


class WebsitePageContentInput(graphene.InputObjectType):
    content_included = graphene.Boolean(default=False)
    excluded_tags = graphene.List(graphene.String)


class WebsitePageFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    name = graphene.String()
    url = graphene.String()


class WebsitePageQuery(graphene.ObjectType):
    website_page = graphene.Field(
        WebsitePageI,
        required=True,
        id=graphene.Int(),
        content_rendering=graphene.Argument(WebsitePageContentInput, default_value={})
    )
    website_pages = graphene.Field(
        WebsitePagesI,
        filter=graphene.Argument(WebsitePageFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        content_rendering=graphene.Argument(WebsitePageContentInput, default_value={}),
    )

    def resolve_website_page(self, info, id, content_rendering):
        env = info.context["env"]
        page = env["website.page"].browse(id).sudo()
        website = get_website(env)
        if page.website_id and page.website_id != website:
            raise GraphQLError("Website page does not exist!")
        content = ''
        if content_rendering.get('content_included'):
            content = page.render_vsf_page(**content_rendering)
        return WebsitePageWithContent(
            website_page=page,
            content=content
        )

    @staticmethod
    def resolve_website_pages(
        self, info, filter, current_page, page_size, content_rendering
    ):
        env = info.context["env"]
        WebsitePage = env['website.page'].sudo()
        domain = WebsitePage.prepare_vsf_domain(**filter)
        offset = get_offset(current_page, page_size)
        website_pages = WebsitePage.search(domain, offset=offset, limit=page_size)
        total_count = WebsitePage.search_count(domain)
        if content_rendering.get('content_included'):
            contents = [p.render_vsf_page(**content_rendering) for p in website_pages]
        else:
            contents = [''] * len(website_pages)
        return WebsitePageList(
            website_pages=website_pages,
            total_count=total_count,
            contents=contents
        )
