from django import template
from django.db.models.query import QuerySet
from django.core.paginator import Page


register = template.Library()


@register.filter
def get_likes(queryset: QuerySet) -> list:
    return [like.user.pk for like in queryset]


@register.filter
def get_tags(queryset: QuerySet) -> str:
    return " ".join([t.tag.tag for t in queryset])


@register.filter
def is_page(page_obj) -> bool:
    return isinstance(page_obj, Page)


@register.filter
def get_fullname(page_obj) -> str:
    if isinstance(page_obj, Page):
        fullname = " ".join([page_obj[0].user.first_name, page_obj[0].user.last_name])
    else:
        fullname = " ".join([page_obj.first_name, page_obj.last_name])
    return fullname


@register.filter
def get_bio(page_obj) -> str:
    if isinstance(page_obj, Page):
        bio = page_obj[0].user.bio
    else:
        bio = page_obj.bio
    return bio


@register.filter
def get_avatar(page_obj) -> str:
    if isinstance(page_obj, Page):
        avatar = page_obj[0].user.avatar.url
    else:
        avatar = page_obj.avatar.url
    return avatar


@register.filter
def check_avatar(page_obj) -> str:
    if isinstance(page_obj, Page):
        return page_obj[0].user.avatar
    else:
        return page_obj.avatar
