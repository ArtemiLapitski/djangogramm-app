from django.urls import path
from django.contrib.auth.decorators import login_required
from feed.views import Feed, Profile, CreatePost, Like, Follow, AWSLambdaWebhook

urlpatterns = [
    path('', Feed.as_view(), name="feed"),
    path('profile/<int:user_id>', login_required(Profile.as_view()), name="profile"),
    path('create_post/', login_required(CreatePost.as_view()), name="create_post"),
    path('like/', login_required(Like.as_view()), name="like"),
    path('follow/', login_required(Follow.as_view()), name="follow"),
    path('webhook/', AWSLambdaWebhook.as_view(), name="webhook"),
]
