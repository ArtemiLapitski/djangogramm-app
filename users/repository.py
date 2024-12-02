from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository:

    @staticmethod
    def add(email: str, activation_link: str) -> None:
        User.objects.create(email=email, activation_link=activation_link)

    @staticmethod
    def get(user_id: int) -> User:
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
        # return user

    @staticmethod
    def get_date_joined(activation_link: str) -> datetime:
        return User.objects.get(activation_link=activation_link).date_joined

    @staticmethod
    def is_active(activation_link: str) -> bool:
        return User.objects.get(activation_link=activation_link).is_active

    @staticmethod
    def delete(activation_link: str) -> None:
        User.objects.filter(activation_link=activation_link).delete()

    @staticmethod
    def update_avatar(current_path: str, new_path: str) -> None:
        return User.objects.filter(avatar=current_path).update(avatar=new_path)

    @staticmethod
    def get_by_email(email: str) -> User:
        return User.objects.get(email=email)

    @staticmethod
    def get_by_password_reset_link(password_reset_link: str) -> User:
        return User.objects.get(password_reset_link=password_reset_link)

    @staticmethod
    def check_password_reset_link(password_reset_link: str) -> bool:
        return User.objects.filter(password_reset_link=password_reset_link).exists()

    @staticmethod
    def get_password_reset_date(password_reset_link: str) -> datetime:
        return User.objects.get(password_reset_link=password_reset_link).date_password_reset_link

    @staticmethod
    def check_email(email: str) -> bool:
        return User.objects.filter(email=email).exists()
