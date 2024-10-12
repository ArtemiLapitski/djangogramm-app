from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.query import QuerySet
from django.db.models import Q
from users.models import CustomUser
from feed.models import Image, Like, Tag, PostTag, Post, AuthorFollower


class PostRepository:

    @staticmethod
    def get_all_posts() -> QuerySet:
        return (Post.objects.select_related('user').prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')
                .all().order_by('-datetime_created'))

    @staticmethod
    def get_profile_posts(user_id: int) -> QuerySet:
        return Post.objects.select_related('user').prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')\
            .filter(user_id=user_id).order_by('-datetime_created')

    @staticmethod
    def get_feed_posts(follower_id: int) -> QuerySet:
        return (Post.objects.select_related('user').prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')
                .filter(user_id__author__follower=follower_id)
                .union(Post.objects.select_related('user')
                       .prefetch_related('image_set', 'like_set__user', 'posttag_set__tag')
                       .filter(user_id=follower_id))
                .order_by('-datetime_created'))

    @staticmethod
    def get_post_with_likes(post_id: int) -> QuerySet:
        return Post.objects.select_related('user').prefetch_related('like_set__user').get(id=post_id)

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
        return [like.user.pk for like in post.like_set.all()]

    @staticmethod
    def get_tags(post: Post) -> str:
        return " ".join([t.tag.tag for t in post.posttag_set.all()])

    @staticmethod
    def add(user_id: int, body: str) -> Post:
        return Post.objects.create(user_id=user_id, body=body)


class ImageRepository:
    @staticmethod
    def add(image: InMemoryUploadedFile, post: Post) -> None:
        Image.objects.create(image=image, post=post)

    @staticmethod
    def update(current_path: str, new_path: str) -> None:
        return Image.objects.filter(image=current_path).update(image=new_path)


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


class AuthorFollowerRepository:
    @staticmethod
    def add(author_id: int, follower_id: int) -> None:
        AuthorFollower.objects.create(author_id=author_id, follower_id=follower_id)

    @staticmethod
    def delete(author_id: int, follower_id: int) -> None:
        AuthorFollower.objects.filter(author_id=author_id, follower_id=follower_id).delete()

    @staticmethod
    def is_following(author_id: int, follower_id: int) -> bool:
        return AuthorFollower.objects.filter(author_id=author_id, follower_id=follower_id).exists()

    @staticmethod
    def get_all_stats(user_id: int) -> QuerySet:
        return (AuthorFollower.objects.filter(Q(author_id=user_id) | Q(follower_id=user_id))
                .values_list('author_id', 'follower_id'))

    @staticmethod
    def get_followers_stats(author_id: int) -> int:
        return AuthorFollower.objects.filter(author_id=author_id).count()
