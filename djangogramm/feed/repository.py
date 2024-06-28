from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.query import QuerySet
from users.models import CustomUser
from .models import Image, Like, Tag, PostTag, Post


class PostRepository:

    @staticmethod
    def get_all() -> QuerySet:
        return (Post.objects.select_related('user').prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')
                .all().order_by('-datetime_created'))

    @staticmethod
    def get_user_posts(user_id: int) -> QuerySet:
        return Post.objects.select_related('user').prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')\
            .filter(user_id=user_id).order_by('-datetime_created')

    @staticmethod
    def get_id(post: Post) -> int:
        return post.pk

    @staticmethod
    def get_body(post: Post) -> str:
        return post.body

    @staticmethod
    def get_user(post: Post) -> CustomUser:
        return post.user

    @staticmethod
    def get_images(post: Post) -> list:
        return [image.image.url for image in post.image_set.all()]

    @staticmethod
    def get_likes(post: Post) -> list:
        return [" ".join([like.user.first_name, like.user.last_name]) for like in post.like_set.all()]

    @staticmethod
    def get_likes_count(post: Post) -> int:
        return post.like_set.count()

    @staticmethod
    def get_tags(post: Post) -> list:
        return [t.tag.tag for t in post.posttag_set.all()]

    @staticmethod
    def add(user_id: int, body: str) -> Post:
        return Post.objects.create(user_id=user_id, body=body)


class ImageRepository:
    @staticmethod
    def add(image: InMemoryUploadedFile, post: Post) -> None:
        Image.objects.create(image=image, post=post)


class LikeRepository:
    @staticmethod
    def add(post_id: int, user_id: int) -> None:
        Like.objects.create(post_id=post_id, user_id=user_id)

    @staticmethod
    def delete(post_id: int, user_id: int) -> None:
        Like.objects.filter(post_id=post_id, user_id=user_id).delete()

    @staticmethod
    def check_like(post_id: int, user_id: int) -> bool:
        return Like.objects.filter(post_id=post_id, user_id=user_id).exists()


class TagRepository:
    @staticmethod
    def get_or_add(tag: str) -> Tag:
        return Tag.objects.get_or_create(tag=tag)[0]


class PostTagRepository:
    @staticmethod
    def add(tag_id: int, post_id: int) -> None:
        PostTag.objects.create(tag_id=tag_id, post_id=post_id)
