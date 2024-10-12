import json
from django.shortcuts import reverse
from django.test import TestCase, Client
from djangogramm.test_helpers import (create_mock_image, create_test_user, create_test_post, first_user_credentials,
                                      second_user_credentials, third_user_credentials, allowed_image_file_size,
                                      not_allowed_image_file_size)


class TestCreatePost(TestCase):

    def setUp(self):
        self.client = Client()
        self.create_post_url = reverse('create_post')
        self.post_data = {
            'user_id': 1,
            'body': 'some text',
            'tags': ['#tag']
        }

    def test_create_post_not_logged_in(self):
        response = self.client.get(self.create_post_url, follow=True)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_create_post_get(self):
        self.client.login(**first_user_credentials)
        response = self.client.get(self.create_post_url, follow=True)
        self.assertTemplateUsed(response, 'feed/create_post.html')

    def test_create_post_allowed_image(self):
        self.client.login(**first_user_credentials)
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

    def test_create_post_five_allowed_images(self):
        self.client.login(**first_user_credentials)
        image_allowed_1 = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        image_allowed_2 = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        image_allowed_3 = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        image_allowed_4 = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))
        image_allowed_5 = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'body': self.post_data['body'],
            'tags': self.post_data['tags'],
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_allowed_1,
            "form-1-image": image_allowed_2,
            "form-2-image": image_allowed_3,
            "form-3-image": image_allowed_4,
            "form-4-image": image_allowed_5,

        }, follow=True)

        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, self.post_data['tags'][0])
        self.assertContains(response, self.post_data['body'])

    def test_create_post_not_allowed_image_error(self):
        self.client.login(**first_user_credentials)
        image_not_allowed = create_mock_image(target_file_size=not_allowed_image_file_size, image_size=(300, 300))
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'body': self.post_data['body'],
            'tags': 'tags',
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_not_allowed,
            "form-1-image": image_allowed
        }, follow=True)

        self.assertTemplateUsed(response, 'feed/create_post.html')
        self.assertContains(response, "Image file too large ( &gt; 10mb )")
        self.assertContains(response, "Hash mark should be the first symbol")

    def test_create_post_no_body(self):
        self.client.login(**first_user_credentials)
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'tags': self.post_data['tags'],
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_allowed
        }, follow=True)

        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, self.post_data['tags'][0])

    def test_create_post_no_tags(self):
        self.client.login(**first_user_credentials)
        image_allowed = create_mock_image(target_file_size=allowed_image_file_size, image_size=(300, 300))

        response = self.client.post(self.create_post_url, data={
            'body': self.post_data['body'],
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 5,
            "form-MIN_NUM_FORMS": 1,
            "form-MAX_NUM_FORMS": 5,
            "form-0-image": image_allowed
        }, follow=True)

        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, self.post_data['body'])


class TestFeed(TestCase):

    def setUp(self):
        self.client = Client()
        self.feed_url = reverse('feed')

    def test_feed_show_all_posts_not_logged_in(self):
        response = self.client.get(self.feed_url)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Sign Up")
        self.assertContains(response, "class=\"instacard__header-fullname\">"
                                      "\n                    \n                        Author")
        self.assertContains(response, "<img src=\"/static/images/avatar.png\">")
        self.assertContains(response, "Poland!")
        self.assertContains(response, "#poland #traveling #morskieoko")
        self.assertContains(response, "2 likes")
        self.assertContains(response, "i love painting...")
        self.assertContains(response, "More Iceland!!")

    def test_feed_show_own_and_followees_posts_logged_in(self):
        self.client.login(**second_user_credentials)
        response = self.client.get(self.feed_url)
        self.assertTemplateUsed(response, 'feed/feed.html')
        self.assertContains(response, "<span class=\"instacard__header-fullname\">"
                                      "\n                    \n"
                                      "                        <a href=\"/profile/2\">Margaret Thatcher</a>")
        self.assertContains(response, "Poland!")
        self.assertContains(response, "More Iceland!!")
        self.assertNotContains(response, "i love painting...")


class TestProfileLikeFollow(TestCase):

    def setUp(self):
        self.client = Client()

        self.first_user_profile_url = reverse('profile', kwargs={'user_id': 1})
        self.first_user_id = 1
        self.second_user_profile_url = reverse('profile', kwargs={'user_id': 2})
        self.second_user_id = 2
        self.third_user_profile_url = reverse('profile', kwargs={'user_id': 3})
        self.third_user_id = 3

        self.new_user_credentials = {
            'username': 'some_new_email@mail.com',
            'password': '8uhb5thm'}
        new_user = create_test_user(email=self.new_user_credentials['username'],
                                    password=self.new_user_credentials['password'])
        self.new_user_id = new_user.pk
        self.new_user_profile_url = reverse('profile', kwargs={'user_id': self.new_user_id})

        self.follow_url = reverse('follow')
        self.like_url = reverse('like')

    def test_profile_not_logged_in(self):
        response = self.client.get(self.first_user_profile_url, follow=True)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_profile_no_posts(self):
        self.client.login(**self.new_user_credentials)
        response = self.client.get(self.new_user_profile_url, follow=True)
        self.assertTemplateUsed(response, 'feed/profile.html')
        self.assertContains(response, "<div class=\"profile-card__2-col__fullname\"> Test User </div>")
        self.assertContains(response, "<div class=\"profile-card__2-col__bio\"> some bio </div>")
        self.assertContains(response,
                            "Posts:\n                    <div class=\"profile-card__2-col__stats__posts__value\"> 0")
        self.assertContains(
            response, "Followers:\n    <div class=\"profile-card__2-col__stats__followers__value\"> 0")
        self.assertContains(
            response, "Following:\n                    <div class=\"profile-card__2-col__stats__following__value\"> 0")
        self.assertContains(response, "No posts yet")

    def test_profile_with_posts(self):
        self.client.login(**first_user_credentials)
        response = self.client.get(self.first_user_profile_url, follow=True)
        self.assertContains(response, "<div class=\"profile-card__2-col__fullname\"> John Smith </div>")
        self.assertContains(response, "<div class=\"profile-card__2-col__bio\"> Hi, I&#x27;m John! </div>")
        self.assertContains(response,
                            "Posts:\n                    <div class=\"profile-card__2-col__stats__posts__value\"> 2")
        self.assertContains(
            response, "Followers:\n    <div class=\"profile-card__2-col__stats__followers__value\"> 2")
        self.assertContains(
            response, "Following:\n                    <div class=\"profile-card__2-col__stats__following__value\"> 2")
        self.assertContains(response, "More Iceland!!")

    def test_profile_follower_counter(self):
        self.client.login(**third_user_credentials)
        third_user_profile_one_follower = self.client.get(self.third_user_profile_url)
        self.assertTemplateUsed(third_user_profile_one_follower, 'feed/profile.html')
        self.assertContains(third_user_profile_one_follower,
                            "Followers:\n    <div class=\"profile-card__2-col__stats__followers__value\"> 1")

        self.client.logout()
        self.client.login(**second_user_credentials)
        follow_third_user = self.client.post(self.follow_url, data={"author_id": self.third_user_id}, follow=True)
        self.assertIn("Followers:\n    <div class=\"profile-card__2-col__stats__followers__value\"> 2",
                      json.loads(follow_third_user.content)['counter_html'])
        self.assertIn("Unfollow", json.loads(follow_third_user.content)['button_html'])

        third_user_profile_two_followers = self.client.get(self.third_user_profile_url)
        self.assertTemplateUsed(third_user_profile_two_followers, 'feed/profile.html')
        self.assertContains(third_user_profile_two_followers,
                            "Followers:\n    <div class=\"profile-card__2-col__stats__followers__value\"> 2")

    def test_profile_following_counter(self):
        self.client.login(**third_user_credentials)
        third_user_profile_following_two = self.client.get(self.third_user_profile_url)
        self.assertTemplateUsed(third_user_profile_following_two, 'feed/profile.html')
        self.assertContains(third_user_profile_following_two, "Following:\n                    "
                                                "<div class=\"profile-card__2-col__stats__following__value\"> 2")

        unfollow_some_user = self.client.post(self.follow_url, data={"author_id": self.second_user_id})
        self.assertIn("Follow", json.loads(unfollow_some_user.content)['button_html'])

        third_user_profile_following_one = self.client.get(self.third_user_profile_url)
        self.assertTemplateUsed(third_user_profile_following_one, 'feed/profile.html')
        self.assertContains(third_user_profile_following_one, "Following:\n                    "
                                                  "<div class=\"profile-card__2-col__stats__following__value\"> 1")

    def test_profile_posts_counter(self):
        self.client.login(**first_user_credentials)
        first_user_profile_two_posts = self.client.get(self.first_user_profile_url)
        self.assertTemplateUsed(first_user_profile_two_posts, 'feed/profile.html')
        self.assertContains(first_user_profile_two_posts, "Posts:\n                    "
                                      "<div class=\"profile-card__2-col__stats__posts__value\"> 2")

        create_test_post(user_id=1, body="new post for first user", target_file_size=allowed_image_file_size)
        first_user_profile_three_posts = self.client.get(self.first_user_profile_url)
        self.assertTemplateUsed(first_user_profile_three_posts, 'feed/profile.html')
        self.assertContains(first_user_profile_three_posts, "Posts:\n                    "
                                      "<div class=\"profile-card__2-col__stats__posts__value\"> 3")

    def test_follow_yourself_error(self):
        self.client.login(**first_user_credentials)
        response = self.client.post(self.follow_url, data={"author_id": self.first_user_id}, follow=True)
        self.assertTemplateUsed(response, 'message.html')
        self.assertContains(response, "Error occured. Following your own profile is not allowed")

    def test_like_not_logged_in_error(self):
        response = self.client.post(f'/like/{1}', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_like_unlike(self):
        self.client.login(**first_user_credentials)
        new_post = create_test_post(user_id=self.new_user_id, body="new post for new user",
                                    target_file_size=allowed_image_file_size)
        new_user_post_not_liked = self.client.get(self.new_user_profile_url)
        self.assertTemplateUsed(new_user_post_not_liked, 'feed/profile.html')
        self.assertContains(new_user_post_not_liked, "Posts:\n                    "
                                      "<div class=\"profile-card__2-col__stats__posts__value\"> 1")
        self.assertContains(new_user_post_not_liked, "0 likes")
        self.assertContains(new_user_post_not_liked, "<img src=\"/static/images/not_liked.png\">")

        like_ajax_response = self.client.post(self.like_url, data={"post_id": new_post.pk}, follow=True)
        self.assertTemplateUsed(like_ajax_response, 'ajax_likes.html')
        self.assertContains(like_ajax_response, "1 like")
        self.assertContains(like_ajax_response, "<img src=\"/static/images/liked.png\">")

        new_user_post_liked = self.client.get(self.new_user_profile_url)
        self.assertTemplateUsed(new_user_post_liked, 'feed/profile.html')
        self.assertContains(new_user_post_liked, "Posts:\n                    "
                                      "<div class=\"profile-card__2-col__stats__posts__value\"> 1")
        self.assertContains(new_user_post_liked, "1 like")
        self.assertContains(new_user_post_liked, "<img src=\"/static/images/liked.png\">")

        unlike_ajax_response = self.client.post(self.like_url, data={"post_id": new_post.pk}, follow=True)
        self.assertTemplateUsed(unlike_ajax_response, 'ajax_likes.html')
        self.assertContains(unlike_ajax_response, "0 likes")
        self.assertContains(unlike_ajax_response, "<img src=\"/static/images/not_liked.png\">")

        new_user_post_not_liked_again = self.client.get(self.new_user_profile_url)
        self.assertTemplateUsed(new_user_post_not_liked_again, 'feed/profile.html')
        self.assertContains(new_user_post_not_liked_again, "Posts:\n                    "
                                      "<div class=\"profile-card__2-col__stats__posts__value\"> 1")
        self.assertContains(new_user_post_not_liked_again, "0 likes")
        self.assertContains(new_user_post_not_liked_again, "<img src=\"/static/images/not_liked.png\">")
