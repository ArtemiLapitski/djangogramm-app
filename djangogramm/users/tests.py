from datetime import timedelta
from unittest.mock import Mock, patch
from django.shortcuts import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from allauth.socialaccount.models import SocialAccount
from allauth.tests import mocked_response
from djangogramm.test_helpers import (create_mock_image, create_test_user, registration_credentials,
                                      allowed_avatar_file_size, not_allowed_avatar_file_size)
from djangogramm.settings import ACTIVATION_LINK_LIFETIME_IN_WEEKS


class TestRegistration(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_register_post(self):
        response = self.client.post(self.register_url, registration_credentials, follow=True)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, f"Activation link has been sent to {registration_credentials['email']}")

    def test_register_invalid_email(self):
        invalid_credentials = {
            'email': 'some_email',
        }
        response = self.client.post(self.register_url, invalid_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/registration.html')
        self.assertContains(response, "Enter a valid email address.")

    def test_register_user_exists(self):
        invalid_credentials = {
            'email': 'jsmith@mail.com',
        }
        response = self.client.post(self.register_url, invalid_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/registration.html')
        self.assertContains(response, "User under this email already exists")

    def test_registration_email_sending(self):
        self.client.post(self.register_url, registration_credentials, follow=True)
        self.user_activation_link = (get_user_model().objects.get(email=registration_credentials['email'])
                                     .activation_link)
        actual_body = mail.outbox[0].body
        expected_body = (f"\nHi,\nPlease click on the link to confirm your registration"
                         f"\nhttp://example.com/users/activate/{self.user_activation_link}\n")
        self.assertEquals(actual_body, expected_body)

    def test_register_no_email(self):
        response = self.client.post(self.register_url, follow=True)
        self.assertTemplateUsed(response, 'users/registration.html')
        self.assertContains(response, "This field is required.")


class TestActivation(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.client.post(self.register_url, registration_credentials, follow=True)
        self.user_activation_link = (get_user_model().objects.get(email=registration_credentials['email'])
                                     .activation_link)
        self.activation_url = reverse('activate', args=[self.user_activation_link])

    def test_activation_get(self):
        response = self.client.get(self.activation_url)
        self.assertTemplateUsed(response, 'users/activation.html')

    def test_activation_get_wrong_link_error(self):
        wrong_activation_url = reverse('activate', args=['wrong_unique_link'])
        response = self.client.get(wrong_activation_url)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Activation link is invalid")

    def test_activation_already_activated_user_error(self):
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        self.client.post(self.activation_url, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar,
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        })
        response = self.client.get(self.activation_url)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "The user has already been activated. You can log in now.")

    def test_activation_expired_link_error(self):
        user = get_user_model().objects.get(email=registration_credentials['email'])
        user.date_joined = user.date_joined - timedelta(weeks=(ACTIVATION_LINK_LIFETIME_IN_WEEKS + 1))
        user.save()
        self.assertTrue(get_user_model().objects.filter(email=registration_credentials['email']).exists())
        response = self.client.get(self.activation_url)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Activation link has expired. Please register again")
        self.assertFalse(get_user_model().objects.filter(email=registration_credentials['email']).exists())

    def test_activation_no_password_error(self):
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        response = self.client.post(self.activation_url, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar,
        })
        self.assertTemplateUsed(response, 'users/activation.html')
        self.assertContains(response, "This field is required.")

    def test_activation_post(self):
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        response = self.client.post(self.activation_url, follow=True, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar,
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        })
        self.assertTemplateUsed(response, 'feed/feed.html')

    def test_activation_post_failed_validation_error(self):
        avatar_not_allowed = create_mock_image(target_file_size=not_allowed_avatar_file_size, image_size=(200, 200))
        response = self.client.post(self.activation_url, data={
            'first_name': 'John!',
            'last_name': 'Smith!',
            'avatar': avatar_not_allowed,
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        })
        self.assertTemplateUsed(response, 'users/activation.html')
        self.assertContains(response, "Image file too large ( &gt; 10mb )")
        self.assertContains(response, "Only letters, numbers and spaces are allowed")


class TestLoginLogout(TestCase):

    def setUp(self):
        self.client = Client()
        create_test_user(email=registration_credentials['email'], password=registration_credentials['password1'])

        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.feed_url = reverse('feed')
        self.login_credentials = {
            'username': registration_credentials['email'],
            'password': registration_credentials['password1']}

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_post(self):
        response = self.client.post(self.login_url, data=self.login_credentials, follow=True)
        self.assertTemplateUsed(response, 'feed/feed.html')

    def test_login_post_wrong_credentials_error(self):
        response = self.client.post(self.login_url, data={
            'username': 'wrong_email@mail.com',
            'password': registration_credentials['password1']}
            , follow=True)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, "Please enter a correct email and password. "
                                      "Note that both fields may be case-sensitive")

    def test_logout(self):
        logged_in = self.client.login(**self.login_credentials)
        self.assertTrue(logged_in)

        response = self.client.get(self.feed_url)
        self.assertContains(response, "Logout")
        self.assertTemplateUsed(response, 'feed/feed.html')

        response = self.client.get(self.logout_url, follow=True)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "Sign In")


class TestSocialLogin(TestCase):

    def setUp(self):
        self.client = Client()
        self.avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        self.activation_data = {
            'first_name': 'Raymond',
            'last_name': 'Penners',
            'bio': 'some bio',
            'avatar': self.avatar,
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }

    def test_github_login(self):
        response = self.client.post(reverse('github_login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://github.com/login/oauth/authorize?client_id=my_client_id", response.url)

    def test_google_login(self):
        response = self.client.post(reverse('google_login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth?client_id=my_client_id", response.url)

    def test_google_callback(self):
        self.client.cookies.load({"g_csrf_token": "csrf"})
        with patch(
            "allauth.socialaccount.internal.jwtkit.jwt.get_unverified_header"
        ) as g_u_h:
            with mocked_response({"dummykid": "-----BEGIN CERTIFICATE-----"}):
                with patch(
                    "allauth.socialaccount.internal.jwtkit.load_pem_x509_certificate"
                ) as load_pem:
                    with patch(
                        "allauth.socialaccount.internal.jwtkit.jwt.decode"
                    ) as decode:
                        decode.return_value = {
                            "iss": "https://accounts.google.com",
                            "aud": "client_id",
                            "sub": "123sub",
                            "hd": "example.com",
                            "email": "raymond@example.com",
                            "email_verified": True,
                            "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
                            "name": "Raymond Penners",
                            "picture": "https://lh5.googleusercontent.com/photo.jpg",
                            "given_name": "Raymond",
                            "family_name": "Penners",
                            "locale": "en",
                            "iat": 123,
                            "exp": 456,
                        }
                        g_u_h.return_value = {
                            "alg": "RS256",
                            "kid": "dummykid",
                            "typ": "JWT",
                        }
                        pem = Mock()
                        load_pem.return_value = pem
                        pem.public_key.return_value = "key"
                        resp = self.client.post(
                            reverse("google_login_by_token"),
                            {"credential": "dummy", "g_csrf_token": "csrf"},
                        )
                        self.assertEqual(resp.status_code, 302)
                        socialaccount = SocialAccount.objects.get(uid="123sub")
                        self.assertEqual(socialaccount.user.email, "raymond@example.com")
                        expected_url = '/users/activate/' + socialaccount.user.activation_link
                        self.assertEqual(expected_url, resp.url)

                        activate_response = self.client.post(resp.url, follow=True, data=self.activation_data)
                        self.assertTemplateUsed(activate_response, 'feed/feed.html')

                        self.assertEqual(int(self.client.session['_auth_user_id']), socialaccount.user.pk)
