from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.query import QuerySet
from .repository import PostRepository, TagRepository, LikeRepository, ImageRepository, PostTagRepository
from users.repository import UserRepository
from .models import Post


class PostService:

    @staticmethod
    def posts_to_list_of_dicts(posts: QuerySet) -> list:
        posts_list = []

        for post in posts:
            user = PostRepository().get_user(post)
            post_dict = {
                'post_id': PostRepository.get_id(post),
                'user_id': UserRepository.get_id(user),
                'fullname': UserRepository.get_fullname(user),
                'body': PostRepository.get_body(post),
                'avatar': UserRepository.get_avatar(user),
                'images': PostRepository.get_images(post),
                'likes': PostRepository.get_likes(post),
                'likes_count': PostRepository.get_likes_count(post),
                'tags': PostRepository.get_tags(post)
            }
            posts_list.append(post_dict)

        return posts_list

    @staticmethod
    def get_posts() -> list:
        posts = PostRepository.get_all()
        return PostService.posts_to_list_of_dicts(posts)

    @staticmethod
    def get_user_posts(user_id: int) -> list:
        posts = PostRepository.get_user_posts(user_id)
        return PostService.posts_to_list_of_dicts(posts)

    @staticmethod
    def create_post(user_id: int, body: str, tags: list) -> Post:
        post = PostRepository.add(user_id=user_id, body=body)
        if tags:
            for tag in tags:
                tag = TagRepository.get_or_add(tag=tag)
                PostTagRepository.add(tag_id=tag.pk, post_id=post.pk)
        return post


class LikeService:

    @staticmethod
    def like(post_id: int, user_id: int) -> None:
        LikeRepository.add(post_id=post_id, user_id=user_id)

    @staticmethod
    def check_like(post_id: int, user_id: int) -> bool:
        return LikeRepository.check_like(post_id=post_id, user_id=user_id)

    @staticmethod
    def unlike(post_id: int, user_id: int) -> None:
        LikeRepository.delete(post_id=post_id, user_id=user_id)


class ImageService:

    @staticmethod
    def add(image: InMemoryUploadedFile, post: Post) -> None:
        ImageRepository.add(image=image, post=post)
