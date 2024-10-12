import json
from django.shortcuts import reverse
from django.test import TestCase, Client
from djangogramm.test_helpers import create_mock_image, allowed_image_file_size, not_allowed_image_file_size
from djangogramm.settings import AWS_WEBHOOK_TOKEN
from feed.forms import ImageForm, ImageFormSet, PostForm
from feed.models import Image
from users.models import CustomUser


class TestImageFormsetAndForm(TestCase):
    def test_valid_form_and_formset(self):
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        data = {
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5
        }
        formset = ImageFormSet(data, files={"form-0-image": image_allowed})
        form = ImageForm(files={'image': image_allowed})
        self.assertTrue(formset.is_valid())
        self.assertTrue(form.is_valid())

    def test_invalid_form_and_formset(self):
        image_not_allowed = create_mock_image(target_file_size=not_allowed_image_file_size, image_size=(300, 300))
        data = {
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5
        }
        formset = ImageFormSet(data, files={"form-0-image": image_not_allowed})
        form = ImageForm(files={'image': image_not_allowed})
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{'image': ['Image file too large ( > 10mb )']}, {}, {}, {}, {}])
        self.assertFalse(form.is_valid())
        self.assertEqual(['Image file too large ( > 10mb )'], form.errors['image'])

    def test_no_image(self):
        data = {
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5
        }
        formset = ImageFormSet(data)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{'image': ['This field is required.']}, {}, {}, {}, {}])


class TestPostForm(TestCase):
    def test_valid_form(self):
        data = {
            'body': 'some text',
            'tags': '#tag #tags'
        }
        form = PostForm(data)
        self.assertTrue(form.is_valid())

    def test_tags_double_space_error(self):
        data = {
            'body': 'some text',
            'tags': '#tag  #tags'
        }
        form = PostForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(['Tags should be separated by single space character'], form.errors['tags'])

    def test_tags_letters_only_error(self):
        tags = ['#tag #tag2', '#tag #tag!', '#ta_g #happy', '#tag ##tag']
        for tag in tags:
            data = {
                'body': 'some text',
                'tags': tag
            }
            form = PostForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(['Only letters are allowed after a hash mark'], form.errors['tags'])

    def test_repeating_tags(self):
        data = {
            'body': 'some text',
            'tags': '#tag #tag'
        }
        form = PostForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(['Tags cannot repeat for a single post'], form.errors['tags'])

    def test_no_tags(self):
        data = {
            'body': 'some text',
        }
        form = PostForm(data)
        self.assertTrue(form.is_valid())

    def test_no_body(self):
        data = {
            'tags': '#tag #tags'
        }
        form = PostForm(data)
        self.assertTrue(form.is_valid())


class TestWebhook(TestCase):

    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('webhook')
        self.image_path = str(Image.objects.get(pk=1).image)
        self.avatar_path = str(CustomUser.objects.get(pk=1).avatar)

    def test_webhook_make_thumbnail_image_success(self):
        thumbnail_path = 'thumbnails/' + self.image_path
        data = {
            'token': AWS_WEBHOOK_TOKEN,
            'make_thumbnail': {
                'original': self.image_path,
                'thumbnail': thumbnail_path
            }
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertContains(response, b'{"message": "make_thumbnail operation has been completed"}')
        self.assertEqual(response.status_code, 200)
        new_image_path = str(Image.objects.get(pk=1).image)
        self.assertEqual(new_image_path, thumbnail_path)

    def test_webhook_make_thumbnail_avatar_success(self):
        thumbnail_path = 'thumbnails/' + self.avatar_path
        data = {
            'token': AWS_WEBHOOK_TOKEN,
            'make_thumbnail': {
                'original': self.avatar_path,
                'thumbnail': thumbnail_path
            }
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertContains(response, b'{"message": "make_thumbnail operation has been completed"}')
        self.assertEqual(response.status_code, 200)
        new_avatar_path = str(CustomUser.objects.get(pk=1).avatar)
        self.assertEqual(new_avatar_path, thumbnail_path)

    def test_webhook_make_thumbnail_image_not_found_error(self):
        image_path = 'images/some_image'
        thumbnail_path = 'thumbnails/' + image_path
        data = {
            'token': AWS_WEBHOOK_TOKEN,
            'make_thumbnail': {
                'original': image_path,
                'thumbnail': thumbnail_path
            }
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.content, b'{"message": "Image was not found"}')
        self.assertEqual(response.status_code, 400)

    def test_webhook_make_thumbnail_avatar_not_found_error(self):
        avatar_path = 'avatars/some_avatar'
        thumbnail_path = 'thumbnails/' + avatar_path
        data = {
            'token': AWS_WEBHOOK_TOKEN,
            'make_thumbnail': {
                'original': avatar_path,
                'thumbnail': thumbnail_path
            }
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.content, b'{"message": "Image was not found"}')
        self.assertEqual(response.status_code, 400)

    def test_webhook_make_thumbnail_operation_not_found_error(self):
        data = {
            'token': AWS_WEBHOOK_TOKEN,
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.content, b'{"message": "No operation found"}')
        self.assertEqual(response.status_code, 400)

    def test_webhook_make_thumbnail_wrong_token(self):
        thumbnail_path = 'thumbnails/' + self.image_path
        data = {
            'token': 'wrong_token',
            'make_thumbnail': {
                'original': self.image_path,
                'thumbnail': thumbnail_path
            }
        }
        response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.content, b'{"message": "Token is invalid"}')
        self.assertEqual(response.status_code, 400)

    def test_webhook_make_thumbnail_empty_thumbnail_error(self):
        wrong_thumbnails = [None, ""]
        for thumbnail_path in wrong_thumbnails:
            data = {
                'token': AWS_WEBHOOK_TOKEN,
                'make_thumbnail': {
                    'original': self.image_path,
                    'thumbnail': thumbnail_path
                }
            }
            response = self.client.post(self.webhook_url, data=json.dumps(data), content_type="application/json")
            self.assertEqual(response.content, b'{"message": "Thumbnail cannot be emtpy"}')
            self.assertEqual(response.status_code, 400)

    def test_webhook_make_thumbnail_no_data(self):
        response = self.client.post(self.webhook_url, data={}, content_type="application/json")
        self.assertEqual(response.content, b'{"message": "Token is invalid"}')
        self.assertEqual(response.status_code, 400)
