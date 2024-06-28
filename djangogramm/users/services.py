from uuid import uuid4
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import RegistrationForm
from djangogramm.settings import ACTIVATION_LINK_LIFETIME_IN_WEEKS
from .repository import UserRepository


class UserService:
    @staticmethod
    def generate_activation_link() -> str:
        activation_link = str(uuid4())
        while UserRepository.check_activation_link(activation_link):
            activation_link = str(uuid4())
        return activation_link

    @staticmethod
    def create_user(form: RegistrationForm, activation_link: str) -> None:
        user = form.save(commit=False)
        user.activation_link = activation_link
        UserRepository.save(user)

    @staticmethod
    def send_email(email: str, domain: str, activation_link: str) -> None:
        subject = 'Registration at DjangoGramm'
        message = render_to_string('users/activation_email.html', {
            'domain': domain,
            'activation_link': activation_link
        })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)

    @staticmethod
    def get_user_data(user_id: int) -> dict:
        user = UserRepository.get_by_id(user_id)
        return {
            'fullname': UserRepository.get_fullname(user),
            'avatar': UserRepository.get_avatar(user),
            'bio': UserRepository.get_bio(user)
        }

    @staticmethod
    def add_and_get_link(email: str) -> str:
        unique_link = UserService.generate_activation_link()
        UserRepository.add(email, unique_link)
        return unique_link

    @staticmethod
    def activate_user(activation_link: str, first_name: str, last_name: str, bio: str = None, avatar: str = None) \
            -> None:
        user = UserRepository.get_by_activation_link(activation_link)
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.avatar = avatar
        user.is_active = True
        UserRepository.save(user)

    @staticmethod
    def check_timestamp(activation_link: str) -> bool:
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
