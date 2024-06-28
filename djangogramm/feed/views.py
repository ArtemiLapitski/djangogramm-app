from django.shortcuts import render, redirect
from django.views import View
from .services import PostService, LikeService, ImageService
from users.services import UserService
from .forms import PostForm, ImageFormSet
from .helpers import get_page_obj


class Feed(View):
    def get(self, request):

        posts = PostService.get_posts()
        page_obj = get_page_obj(posts=posts, page_number=request.GET.get('page'))

        context = {'posts': posts,
                   'page_obj': page_obj,
                   }
        return render(request, 'feed/feed.html', context=context)


class Like(View):
    def get(self, request, post_id):
        user_id = request.user.pk
        if LikeService.check_like(user_id=user_id, post_id=post_id):
            LikeService.unlike(user_id=user_id, post_id=post_id)
        else:
            LikeService.like(user_id=user_id, post_id=post_id)

        return redirect(request.GET.get('url'))


class Profile(View):
    def get(self, request, user_id):
        user_data = UserService.get_user_data(user_id)
        posts = PostService.get_user_posts(user_id)
        page_obj = get_page_obj(posts=posts, page_number=request.GET.get('page'))

        context = {
            'posts': posts,
            'page_obj': page_obj,
                   }

        return render(request, 'feed/profile.html', context=context | user_data)


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
        else:
            return render(request, 'feed/create_post.html', context={"post_form": post_form,
                                                                     "image_formset": image_formset})
