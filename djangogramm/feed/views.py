import json
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.template.loader import render_to_string
from feed.services import PostService, LikeService, ImageService, AuthorFollowerService
from feed.forms import PostForm, ImageFormSet
from feed.helpers import get_page_obj, get_paginator
from feed.models import Post
from users.services import UserService
from djangogramm.settings import AWS_WEBHOOK_TOKEN


class Feed(View):
    def get(self, request):
        if request.user.is_authenticated:
            posts = PostService.get_feed_posts(request.user.pk)
            page_obj = get_page_obj(posts=posts, page_number=request.GET.get('page'))
        else:
            posts = PostService.get_all_posts()
            page_obj = get_page_obj(posts=posts, page_number=request.GET.get('page'))
        context = {'page_obj': page_obj}
        return render(request, 'feed/feed.html', context=context)


class Like(View):

    def get(self, request):
        p = PostService.get_post_with_likes(6)
        context = {'p': p}
        return render(request, 'ajax_likes.html', context)

    def post(self, request):
        user_id = request.user.pk
        post_id = request.POST['post_id']
        if LikeService.check_like(user_id=user_id, post_id=post_id):
            LikeService.unlike(user_id=user_id, post_id=post_id)
        else:
            LikeService.like(user_id=user_id, post_id=post_id)
        post = PostService.get_post_with_likes(post_id)
        context = {'p': post}
        return render(request, 'ajax_likes.html', context)


class Profile(View):
    def get(self, request, user_id):
        stats = AuthorFollowerService.get_all_stats(author_id=user_id, follower_id=request.user.pk)
        followers_data = {
                'followers': stats['followers'],
                'followees': stats['followees'],
                'is_following': stats['is_following']
                       }
        if Post.objects.filter(user_id=user_id).exists():
            posts = PostService.get_profile_posts(user_id)
            p = get_paginator(posts=posts)
            page_obj = p.get_page(request.GET.get('page'))
            context = {
                'page_obj': page_obj,
                'author_id': user_id,
                'posts_amount': p.count
                       }
            return render(request, 'feed/profile.html', context=context | followers_data)
        else:
            context = {
                'page_obj': UserService.get(user_id=user_id),
                'author_id': user_id,
                'posts_amount': 0
                       }
            return render(request, 'feed/profile.html', context=context | followers_data)


class CreatePost(View):
    def get(self, request):
        post_form = PostForm()
        image_formset = ImageFormSet()
        return render(request, 'feed/create_post.html', context={"post_form": post_form,
                                                                 "image_formset": image_formset})

    def post(self, request):
        post_form = PostForm(request.POST)
        image_formset = ImageFormSet(request.POST, files=request.FILES)
        if post_form.is_valid() and image_formset.is_valid():
            post = PostService.create_post(
                user_id=request.user.pk,
                body=post_form.cleaned_data['body'],
                tags=post_form.cleaned_data['tags']
            )
            for _, image in request.FILES.items():
                ImageService.add(image=image, post=post)
            return redirect('feed')
        return render(request, 'feed/create_post.html', context={"post_form": post_form,
                                                                 "image_formset": image_formset})


class Follow(View):
    def post(self, request):
        author_id = int(request.POST['author_id'])
        follower_id = request.user.pk
        if follower_id != author_id:
            if AuthorFollowerService.is_following(author_id=author_id, follower_id=follower_id):
                AuthorFollowerService.unfollow(author_id=author_id, follower_id=follower_id)
                is_following = False
            else:
                AuthorFollowerService.follow(author_id=author_id, follower_id=follower_id)
                is_following = True

            button_context = {'author_id': author_id, 'is_following': is_following}
            button_html = render_to_string('feed/ajax_follow_button.html', context=button_context, request=request)

            followers = AuthorFollowerService.get_followers_stats(author_id)
            counter_context = {'followers': followers}
            counter_html = render_to_string('feed/ajax_followers_counter.html', context=counter_context,
                                            request=request)

            return JsonResponse({'button_html': button_html, 'counter_html': counter_html})

        return render(request, 'message.html',
                      {'message': "Error occured. Following your own profile is not allowed"})


@method_decorator(csrf_exempt, name='dispatch')
class AWSLambdaWebhook(View):
    def post(self, request):
        data = json.loads(request.body)
        token = data.get('token')
        if token == AWS_WEBHOOK_TOKEN:
            make_thumbnail_data = data.get('make_thumbnail')
            if make_thumbnail_data:

                original = make_thumbnail_data['original']
                thumbnail = make_thumbnail_data['thumbnail']

                if thumbnail is None or thumbnail == "":
                    return JsonResponse(status=400, data={'message': "Thumbnail cannot be emtpy"})

                if "avatars" in original:
                    instances = UserService.update_avatar(current_path=original, new_path=thumbnail)
                else:
                    instances = ImageService.update(current_path=original, new_path=thumbnail)

                if instances == 0:
                    return JsonResponse(status=400, data={'message': "Image was not found"})

                return JsonResponse(status=200, data={'message': 'make_thumbnail operation has been completed'})
            return JsonResponse(status=400, data={'message': 'No operation found'})
        return JsonResponse(status=400, data={'message': 'Token is invalid'})
