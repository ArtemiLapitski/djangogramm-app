from uuid import uuid4
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from users.repository import UserRepository
from djangogramm.settings import ACTIVATION_LINK_LIFETIME_IN_WEEKS, PASSWORD_RESET_LINK_LIFETIME_IN_WEEKS


User = get_user_model()


class UserService:

    @staticmethod
    def get(user_id: int) -> User:
        return UserRepository.get(user_id)

    @staticmethod
    def generate_activation_link() -> str:
        activation_link = str(uuid4())
        while UserRepository.check_activation_link(activation_link):
            activation_link = str(uuid4())
        return activation_link

    @staticmethod
    def create_user(email: str, activation_link: str) -> None:
        UserRepository.add(email, activation_link)

    @staticmethod
    def send_activation_email(email: str, domain: str, activation_link: str) -> None:
        subject = 'Registration at DjangoGramm'
        message = render_to_string('users/activation_email.html', {
            'domain': domain,
            'activation_link': activation_link
        })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)

    @staticmethod
    def activate_user(activation_link: str, first_name: str, last_name: str, password1: str, bio: str = None, avatar: str = None, **kwargs) \
            -> None:
        user = UserRepository.get_by_activation_link(activation_link)
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.avatar = avatar
        user.is_active = True
        user.set_password(password1)
        UserRepository.save(user)
        return user

    @staticmethod
    def check_activation_timestamp(activation_link: str) -> bool:
        timestamp = UserRepository.get_date_joined(activation_link)
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        elapsed = now - timestamp
        return elapsed < timedelta(weeks=ACTIVATION_LINK_LIFETIME_IN_WEEKS)

    @staticmethod
    def check_activation_link(activation_link: str) -> bool:
        return UserRepository.check_activation_link(activation_link)

    @staticmethod
    def is_active(activation_link: str) -> bool:
        return UserRepository.is_active(activation_link)

    @staticmethod
    def delete(activation_link: str) -> None:
        UserRepository.delete(activation_link)

    @staticmethod
    def update_avatar(current_path: str, new_path: str) -> None:
        return UserRepository.update_avatar(current_path=current_path, new_path=new_path)

    @staticmethod
    def generate_password_reset_link() -> str:
        password_reset_link = str(uuid4())
        while UserRepository.check_password_reset_link(password_reset_link):
            password_reset_link = str(uuid4())
        return password_reset_link

    @staticmethod
    def add_password_reset_link(email: str) -> str:
        password_reset_link = UserService.generate_password_reset_link()

        user = UserRepository.get_by_email(email)

        user.password_reset_link = password_reset_link
        user.date_password_reset_link = datetime.utcnow().replace(tzinfo=timezone.utc)

        UserRepository.save(user)
        return password_reset_link

    @staticmethod
    def send_password_reset_email(email: str, domain: str, password_reset_link: str) -> None:
        subject = 'Reset Email at DjangoGramm'
        message = render_to_string('users/password_reset_email.html', {
            'domain': domain,
            'password_reset_link': password_reset_link
        })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)

    @staticmethod
    def reset_password(password_reset_link: str, password: str) -> None:
        user = UserRepository.get_by_password_reset_link(password_reset_link)
        user.set_password(password)
        user.password_reset_link = None
        user.date_password_reset_link = None
        UserRepository.save(user)

    @staticmethod
    def check_password_reset_link(password_reset_link: str) -> bool:
        return UserRepository.check_password_reset_link(password_reset_link)

    @staticmethod
    def check_password_reset_timestamp(password_reset_link: str) -> bool:
        timestamp = UserRepository.get_password_reset_date(password_reset_link)
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        elapsed = now - timestamp
        return elapsed < timedelta(weeks=PASSWORD_RESET_LINK_LIFETIME_IN_WEEKS)

    @staticmethod
    def check_email(email: str) -> bool:
        return UserRepository.check_email(email)
