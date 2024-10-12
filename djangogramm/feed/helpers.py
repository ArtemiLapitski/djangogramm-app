from django.core.paginator import Paginator, Page
from django.db.models.query import QuerySet
from djangogramm.settings import POSTS_PER_PAGE


def get_paginator(posts: QuerySet) -> Paginator:
    return Paginator(posts, POSTS_PER_PAGE)


def get_page_obj(posts: QuerySet, page_number: str) -> Page:
    p = get_paginator(posts)
    return p.get_page(page_number)
