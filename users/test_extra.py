from datetime import timedelta
from django.shortcuts import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from users.forms import RegistrationForm, ActivationForm
from djangogramm.test_helpers import (create_mock_image, first_user_credentials, second_user_credentials,
                                      registration_credentials, allowed_avatar_file_size, not_allowed_avatar_file_size)
from djangogramm.settings import PASSWORD_RESET_LINK_LIFETIME_IN_WEEKS


class TestPasswordReset(TestCase):

    def setUp(self):
        self.client = Client()
        self.request_password_reset_url = reverse('request_reset')

        self.client.post(self.request_password_reset_url, {'email': first_user_credentials['username']})
        self.password_reset_link = (get_user_model().objects.get(email=first_user_credentials['username'])
                                    .password_reset_link)

        self.password_reset_url = reverse('reset', args=[self.password_reset_link])
        self.login_url = reverse('login')

        self.new_password_data = {'password1': 'newpassword123', 'password2': 'newpassword123'}

    def test_request_password_reset_get(self):
        response = self.client.get(self.request_password_reset_url)
        self.assertTemplateUsed(response, 'users/password_reset.html')

    def test_request_password_reset_post(self):
        self.assertFalse(get_user_model().objects.get(email=second_user_credentials['username']).password_reset_link)
        self.assertFalse(get_user_model().objects.get(email=second_user_credentials['username'])
                         .date_password_reset_link)

        response = self.client.post(self.request_password_reset_url, {'email': second_user_credentials['username']}
                                    , follow=True)

        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Link for password reset has been sent to your email")
        self.assertTrue(get_user_model().objects.get(email=second_user_credentials['username']).password_reset_link)
        self.assertTrue(get_user_model().objects.get(email=second_user_credentials['username']).date_password_reset_link)

    def test_request_password_reset_post_invalid_email(self):
        response = self.client.post(self.request_password_reset_url, {'email': 'email_not_exist@mail.com'}, follow=True)
        self.assertTemplateUsed(response, 'users/password_reset.html')
        self.assertContains(response, "Email is not registered")

    def test_password_reset_email_sending(self):
        actual_body = mail.outbox[0].body
        expected_body = (f"\nHi,\nPlease click on the link to reset your password"
                         f"\nhttp://example.com/users/reset/{self.password_reset_link}\n")
        self.assertEquals(actual_body, expected_body)

    def test_reset_password_link_correct(self):
        response = self.client.get(self.password_reset_url)
        self.assertTemplateUsed(response, 'users/password_reset.html')
        self.assertContains(response, "New password")
        self.assertContains(response, "Confirm new password")

    def test_reset_password_link_not_valid_error(self):
        response = self.client.get(reverse('reset', args=['not_valid_link']))
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Link is invalid")

    def test_reset_password_link_expired_error(self):
        user = get_user_model().objects.get(email=first_user_credentials['username'])
        user.date_password_reset_link = (user.date_password_reset_link -
                                         timedelta(weeks=(PASSWORD_RESET_LINK_LIFETIME_IN_WEEKS + 1)))
        user.save()
        response = self.client.get(self.password_reset_url)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Link has already expired")

    def test_password_reset(self):
        response = self.client.post(self.password_reset_url, data=self.new_password_data, follow=True)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Password has been changed. You can sign in now")
        user = get_user_model().objects.get(email=first_user_credentials['username'])
        self.assertEqual(user.password_reset_link, None)
        self.assertEqual(user.date_password_reset_link, None)

    def test_login_old_password_error(self):
        self.client.post(self.password_reset_url, data=self.new_password_data, follow=True)
        response = self.client.post(self.login_url, data=first_user_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, "Please enter a correct email and password.")

    def test_login_new_password_success(self):
        self.client.post(self.password_reset_url, data=self.new_password_data, follow=True)
        response = self.client.post(self.login_url, data={
            'username': first_user_credentials['username'],
            'password': self.new_password_data['password1']
        }, follow=True)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "Logout")


class TestRegistrationForm(TestCase):

    def test_valid_form(self):
        form = RegistrationForm(registration_credentials)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = RegistrationForm(data={
            'email': 'some_email'
        })
        self.assertFalse(form.is_valid())


class TestActivationForm(TestCase):

    def test_valid_avatar(self):
        avatar_allowed = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        form = ActivationForm(data={
            'first_name': 'John',
            "last_name": 'Smith',
            "bio": "some_bio",
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        },
            files={"avatar": avatar_allowed}
        )
        self.assertTrue(form.is_valid())

    def test_invalid_avatar(self):
        avatar_not_allowed = create_mock_image(target_file_size=not_allowed_avatar_file_size, image_size=(200, 200))
        form = ActivationForm(data={
            'first_name': 'John',
            "last_name": 'Smith',
            "bio": "some_bio",
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        },
            files={"avatar": avatar_not_allowed}
        )
        self.assertFalse(form.is_valid())

    def test_missing_first_name(self):
        form = ActivationForm(data={
            "last_name": 'Smith',
            "bio": "some_bio",
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['first_name'])

    def test_missing_last_name(self):
        form = ActivationForm(data={
            'first_name': 'John',
            "bio": "some_bio",
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['last_name'])

    def test_missing_password(self):
        form = ActivationForm(data={
            'first_name': 'John',
            "bio": "some_bio"
        }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['password1'])
        self.assertIn('This field is required.', form.errors['password2'])

    def test_first_name_validation(self):
        allowed_names = ['John', 'John Maria', "John-Maria 1"]
        for name in allowed_names:
            form = ActivationForm(data={
                'first_name': name,
                "last_name": 'Smith',
                'password1': '8uhb5thm',
                'password2': '8uhb5thm'
            })
            self.assertTrue(form.is_valid())

    def test_first_name_validation_error(self):
        not_allowed_names = ['John!', 'John/Maria', "John@Maria", "John  Maria"]
        for name in not_allowed_names:
            form = ActivationForm(data={
                'first_name': name,
                "last_name": 'Smith',
                'password1': '8uhb5thm',
                'password2': '8uhb5thm'
            })
            self.assertFalse(form.is_valid())

    def test_second_name_validation(self):
        allowed_surnames = ['John', 'John Maria', "John-Maria 1"]
        for surname in allowed_surnames:
            form = ActivationForm(data={
                'first_name': 'John',
                "last_name": surname,
                'password1': '8uhb5thm',
                'password2': '8uhb5thm'
            })
            self.assertTrue(form.is_valid())

    def test_second_name_validation_error(self):
        not_allowed_surnames = ['John!', 'John/Maria', "John@Maria", "John  Maria"]
        for surname in not_allowed_surnames:
            form = ActivationForm(data={
                'first_name': 'John',
                "last_name": surname,
                'password1': '8uhb5thm',
                'password2': '8uhb5thm'
            })
            self.assertFalse(form.is_valid())
