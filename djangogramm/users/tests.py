from datetime import timedelta
from os.path import join
from shutil import rmtree
from django.shortcuts import reverse
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from PIL import Image
from .forms import RegistrationForm, ActivationForm
from djangogramm.helpers import create_mock_image, create_test_user
from djangogramm.settings import (MAX_AVATAR_FILE_SIZE, TEST_DIR, AVATAR_THUMBNAIL_SIZE,
                                  ACTIVATION_LINK_LIFETIME_IN_WEEKS)


registration_credentials = {
            'email': 'some_email@mail.com',
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }

allowed_avatar_file_size: int = int(MAX_AVATAR_FILE_SIZE / 10)
not_allowed_avatar_file_size: int = MAX_AVATAR_FILE_SIZE + 1


class TestRegistration(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_get(self):
        response = self.client.get(self.register_url)
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_register_post(self):
        response = self.client.post(self.register_url, registration_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/message.html')
        self.assertContains(response, f"Activation link has been sent to {registration_credentials['email']}")

    def test_register_post_invalid_credentials(self):
        invalid_credentials = {
            'email': 'some_email',
            'password1': '8uhb5thmn',
            'password2': '8uhb5thm'
        }
        response = self.client.post(self.register_url, invalid_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/registration.html')
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, "The two password fields didn’t match.")

    def test_email_sending(self):
        self.client.post(self.register_url, registration_credentials, follow=True)
        self.user_activation_link = (get_user_model().objects.get(email=registration_credentials['email'])
                                     .activation_link)
        actual_body = mail.outbox[0].body
        expected_body = (f"\nHi,\nPlease click on the link to confirm your registration"
                         f"\nhttp://testserver/users/activate/{self.user_activation_link}\n")
        self.assertEquals(actual_body, expected_body)

    def test_register_no_email(self):
        invalid_credentials = {
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }
        response = self.client.post(self.register_url, invalid_credentials, follow=True)
        self.assertTemplateUsed(response, 'users/registration.html')
        self.assertContains(response, "This field is required.")

    def test_register_no_password(self):
        invalid_credentials = {
            'email': 'some_email',
            'password1': '8uhb5thm',
        }
        response = self.client.post(self.register_url, invalid_credentials, follow=True)
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
        self.assertTemplateUsed(response, 'users/message.html')
        self.assertContains(response, "Activation link is invalid")

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_activation_get_already_activated_user_error(self):
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        self.client.post(self.activation_url, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar
        })
        response = self.client.get(self.activation_url)
        self.assertTemplateUsed(response, 'users/message.html')
        self.assertContains(response, "The user has already been activated. You can log in now.")

    def test_activation_get_expired_link_error(self):
        date_joined = get_user_model().objects.get(email=registration_credentials['email']).date_joined
        excessive_lifetime_in_weeks = ACTIVATION_LINK_LIFETIME_IN_WEEKS + 1
        excessive_lifetime_timedelta = timedelta(weeks=excessive_lifetime_in_weeks)
        new_date_joined = date_joined - excessive_lifetime_timedelta
        get_user_model().objects.filter(email=registration_credentials['email']).update(date_joined=new_date_joined)
        self.assertTrue(get_user_model().objects.filter(email=registration_credentials['email']).exists())
        response = self.client.get(self.activation_url)
        self.assertTemplateUsed(response, 'users/message.html')
        self.assertContains(response, "Activation link has expired. Please register again")
        self.assertFalse(get_user_model().objects.filter(email=registration_credentials['email']).exists())

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_activation_post(self):
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        response = self.client.post(self.activation_url, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar
        })
        self.assertTemplateUsed(response, 'users/message.html')
        self.assertContains(response, "The user has been activated. You can log in now.")

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_activation_post_failed_validation_error(self):
        avatar_not_allowed = create_mock_image(target_file_size=not_allowed_avatar_file_size, image_size=(200, 200))
        response = self.client.post(self.activation_url, data={
            'first_name': 'John!',
            'last_name': 'Smith!',
            'avatar': avatar_not_allowed
        })
        self.assertTemplateUsed(response, 'users/activation.html')
        self.assertContains(response, "Image file too large ( &gt; 10mb )")
        self.assertContains(response, "Only letters, numbers and spaces are allowed")

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_avatar_thumbnail(self):
        image_size_gt_thumbnail = tuple([i * 2 for i in AVATAR_THUMBNAIL_SIZE])
        image_name = 'thumbnail_test.jpg'
        avatar = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=image_size_gt_thumbnail,
                                   name=image_name)

        self.client.post(self.activation_url, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'some bio',
            'avatar': avatar
        })

        image = Image.open(join(TEST_DIR, 'media', 'avatars', image_name))
        self.assertEqual(image.size, AVATAR_THUMBNAIL_SIZE)


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
        self.assertContains(response, "Sign in")


class TestRegistrationForm(TestCase):

    def test_valid_form(self):
        form = RegistrationForm(registration_credentials)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = RegistrationForm(data={
            'email': 'some_email',
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        })
        self.assertFalse(form.is_valid())

    def test_not_matching_passwords(self):
        form = RegistrationForm(data={
            'email': 'some_email@mail.com',
            'password1': '8uhb5thm',
            'password2': '8uhb5th'
        })
        self.assertFalse(form.is_valid())


class TestActivationForm(TestCase):

    def test_valid_avatar(self):
        avatar_allowed = create_mock_image(target_file_size=allowed_avatar_file_size, image_size=(200, 200))
        form = ActivationForm(data={
            'first_name': 'John',
            "last_name": 'Smith',
            "bio": "some_bio"
        },
            files={"avatar": avatar_allowed}
        )
        self.assertTrue(form.is_valid())

    def test_invalid_avatar(self):
        avatar_not_allowed = create_mock_image(target_file_size=not_allowed_avatar_file_size, image_size=(200, 200))
        form = ActivationForm(data={
            'first_name': 'John',
            "last_name": 'Smith',
            "bio": "some_bio"
        },
            files={"avatar": avatar_not_allowed}
        )
        self.assertFalse(form.is_valid())

    def test_missing_first_name(self):
        form = ActivationForm(data={
            "last_name": 'Smith',
            "bio": "some_bio"
        }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['first_name'])

    def test_missing_last_name(self):
        form = ActivationForm(data={
            'first_name': 'John',
            "bio": "some_bio"
        }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['last_name'])

    def test_first_name_validation(self):
        allowed_names = ['John', 'John Maria', "John-Maria 1"]
        for name in allowed_names:
            form = ActivationForm(data={
                'first_name': name,
                "last_name": 'Smith'})
            self.assertTrue(form.is_valid())

    def test_first_name_validation_error(self):
        not_allowed_names = ['John!', 'John/Maria', "John@Maria", "John  Maria"]
        for name in not_allowed_names:
            form = ActivationForm(data={
                'first_name': name,
                "last_name": 'Smith'})
            self.assertFalse(form.is_valid())

    def test_second_name_validation(self):
        allowed_surnames = ['John', 'John Maria', "John-Maria 1"]
        for surname in allowed_surnames:
            form = ActivationForm(data={
                'first_name': 'John',
                "last_name": surname})
            self.assertTrue(form.is_valid())

    def test_second_name_validation_error(self):
        not_allowed_surnames = ['John!', 'John/Maria', "John@Maria", "John  Maria"]
        for surname in not_allowed_surnames:
            form = ActivationForm(data={
                'first_name': 'John',
                "last_name": surname})
            self.assertFalse(form.is_valid())


def tearDownModule():
    rmtree(TEST_DIR, ignore_errors=True)
