from os.path import join
from shutil import rmtree
from django.shortcuts import reverse
from django.test import TestCase, Client, override_settings
from PIL import Image
from djangogramm.helpers import create_mock_image, create_test_user
from djangogramm.settings import IMAGE_THUMBNAIL_SIZE, MAX_IMAGE_FILE_SIZE
from .forms import ImageForm, ImageFormSet, PostForm
from .services import PostService, ImageService

login_credentials = {
            'username': 'some_email@mail.com',
            'password': '8uhb5thm'
}


TEST_DIR = 'test_data'

allowed_image_file_size: int = int(MAX_IMAGE_FILE_SIZE / 10)
not_allowed_image_file_size: int = MAX_IMAGE_FILE_SIZE + 1


class TestCreatePost(TestCase):

    def setUp(self):
        self.client = Client()
        self.create_post_url = reverse('create_post')
        user = create_test_user(email=login_credentials['username'], password=login_credentials['password'])
        self.post_data = {
            'user_id': user.pk,
            'body': 'some text',
            'tags': ['#tag']
        }

    def test_create_post_not_logged_in_error(self):
        response = self.client.get(self.create_post_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_create_post_get(self):
        self.client.login(**login_credentials)
        response = self.client.get(self.create_post_url, follow=True)
        self.assertTemplateUsed(response, 'feed/create_post.html')

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_create_post(self):
        self.client.login(**login_credentials)
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'body': self.post_data['body'],
            'tags': self.post_data['tags'],
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_allowed
        }, follow=True)

        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, self.post_data['tags'][0])
        self.assertContains(response, self.post_data['body'])

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_create_post_wrong_data(self):
        self.client.login(**login_credentials)
        image_not_allowed = create_mock_image(target_file_size=not_allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'body': self.post_data['body'],
            'tags': 'tags',
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_not_allowed
        }, follow=True)

        self.assertTemplateUsed(response, 'feed/create_post.html')
        self.assertContains(response, "Image file too large ( &gt; 10mb )")
        self.assertContains(response, "Hash mark should be the first symbol")

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def test_image_thumbnail(self):
        post = PostService.create_post(**self.post_data)

        image_size_gt_thumbnail = tuple([i * 2 for i in IMAGE_THUMBNAIL_SIZE])
        image_name = 'thumbnail_test.jpg'
        image = create_mock_image(target_file_size=allowed_image_file_size, image_size=image_size_gt_thumbnail,
                                  name=image_name)
        ImageService.add(image=image, post=post)
        image = Image.open(join(TEST_DIR, 'media', 'images', image_name))
        self.assertEqual(image.size, IMAGE_THUMBNAIL_SIZE)


class TestFeedLikeProfile(TestCase):

    @override_settings(MEDIA_ROOT=join(TEST_DIR, 'media'))
    def setUp(self):
        self.client = Client()
        self.feed_url = reverse('feed')
        self.create_post_url = reverse('create_post')

        user = create_test_user(email=login_credentials['username'], password=login_credentials['password'])
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        self.post_data = {
            'user_id': user.pk,
            'body': 'some text',
            'tags': ['#tag']
        }
        self.post = PostService.create_post(**self.post_data)
        ImageService.add(image=image_allowed, post=self.post)

        self.like_url = f'/like/{self.post.pk}?url=/'
        self.profile_url = reverse('profile', kwargs={'user_id': user.pk})

    def test_feed_not_logged_in_error(self):
        response = self.client.get(self.feed_url)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "Sign in")
        self.assertContains(response, "Author")
        self.assertContains(response, "Sign up")

    def test_feed(self):
        self.client.login(**login_credentials)
        response = self.client.get(self.feed_url)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "Create Post")
        self.assertContains(response, "Logout")

    def test_like_not_logged_in_error(self):
        response = self.client.get(self.like_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_like(self):
        self.client.login(**login_credentials)
        response = self.client.get(self.like_url, follow=True)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, self.like_url+'">Likes: 1')
        self.assertContains(response, "Create Post")
        self.assertContains(response, "Logout")

    def test_unlike(self):
        self.client.login(**login_credentials)
        response = self.client.get(self.like_url, follow=True)
        self.assertContains(response, self.like_url+'">Likes: 1')
        response = self.client.get(self.like_url, follow=True)
        self.assertContains(response, self.like_url+'">Likes: 0')

    def test_profile_not_logged_in_error(self):
        response = self.client.get(self.profile_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_profile(self):
        self.client.login(**login_credentials)
        response = self.client.get(self.profile_url, follow=True)
        self.assertTemplateUsed(response, 'feed/profile.html')
        self.assertContains(response, "Create Post")
        self.assertContains(response, "Logout")
        self.assertContains(response, self.post_data['tags'][0])
        self.assertContains(response, self.post_data['body'])


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


def tearDownModule():
    rmtree(TEST_DIR, ignore_errors=True)
