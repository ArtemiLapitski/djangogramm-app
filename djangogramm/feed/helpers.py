from django.core.paginator import Paginator, Page
from djangogramm.settings import POSTS_PER_PAGE


def get_page_obj(posts: list, page_number: str) -> Page:
    p = Paginator(posts, POSTS_PER_PAGE)
    return p.get_page(page_number)
