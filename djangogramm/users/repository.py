from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository:

    @staticmethod
    def add(email: str, activation_link: str) -> None:
        User.objects.create(email=email, activation_link=activation_link)

    @staticmethod
    def get_by_id(user_id: int) -> User:
        return User.objects.get(pk=user_id)

    @staticmethod
    def get_id(user: User) -> int:
        return user.pk

    @staticmethod
    def get_avatar(user: User) -> str:
        if user.avatar:
            return user.avatar.url
        else:
            return ''

    @staticmethod
    def get_fullname(user: User) -> str:
        return " ".join([user.first_name, user.last_name])

    @staticmethod
    def get_bio(user: User) -> str:
        return user.bio

    @staticmethod
    def check_activation_link(activation_link: str) -> bool:
        return User.objects.filter(activation_link=activation_link).exists()

    @staticmethod
    def get_by_activation_link(activation_link: str) -> User:
        return User.objects.get(activation_link=activation_link)

    @staticmethod
    def save(user: User) -> None:
        user.save()

    @staticmethod
    def get_date_joined(activation_link: str) -> datetime:
        return User.objects.get(activation_link=activation_link).date_joined

    @staticmethod
    def is_active(activation_link: str) -> bool:
        return User.objects.get(activation_link=activation_link).is_active

    @staticmethod
    def delete(activation_link: str) -> None:
        User.objects.filter(activation_link=activation_link).delete()
