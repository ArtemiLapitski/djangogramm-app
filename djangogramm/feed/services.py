from collections import Counter
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.query import QuerySet
from feed.repository import (PostRepository, TagRepository, LikeRepository, ImageRepository, PostTagRepository,
                             AuthorFollowerRepository)
from feed.models import Post


class PostService:

    @staticmethod
    def get_profile_posts(user_id: int) -> QuerySet:
        return PostRepository.get_profile_posts(user_id)

    @staticmethod
    def get_all_posts() -> QuerySet:
        return PostRepository.get_all_posts()

    @staticmethod
    def get_feed_posts(follower_id: int) -> QuerySet:
        return PostRepository.get_feed_posts(follower_id)

    @staticmethod
    def create_post(user_id: int, body: str, tags: list) -> Post:
        post = PostRepository.add(user_id=user_id, body=body)
        if tags:
            for tag in tags:
                tag = TagRepository.get_or_add(tag=tag)
                PostTagRepository.add(tag_id=tag.pk, post_id=post.pk)
        return post

    @staticmethod
    def get_post_with_likes(post_id: int) -> QuerySet:
        return PostRepository.get_post_with_likes(post_id=post_id)


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

    @staticmethod
    def update(current_path: str, new_path: str) -> None:
        return ImageRepository.update(current_path=current_path, new_path=new_path)


class AuthorFollowerService:

    @staticmethod
    def follow(author_id: int, follower_id: int) -> None:
        AuthorFollowerRepository.add(author_id=author_id, follower_id=follower_id)

    @staticmethod
    def unfollow(author_id: int, follower_id: int) -> None:
        AuthorFollowerRepository.delete(author_id=author_id, follower_id=follower_id)

    @staticmethod
    def is_following(author_id: int, follower_id: int) -> bool:
        return AuthorFollowerRepository.is_following(author_id=author_id, follower_id=follower_id)

    @staticmethod
    def get_all_stats(author_id: int, follower_id: int) -> dict:
        author_follower_data = AuthorFollowerRepository.get_all_stats(user_id=author_id)
        authors_counter = Counter(author for author, _ in author_follower_data)
        followers_counter = Counter(follower for _, follower in author_follower_data)
        return {'followers': authors_counter[author_id],
                'followees': followers_counter[author_id],
                'is_following': (author_id, follower_id) in author_follower_data
                }

    @staticmethod
    def get_followers_stats(author_id: int) -> int:
        return AuthorFollowerRepository.get_followers_stats(author_id=author_id)
