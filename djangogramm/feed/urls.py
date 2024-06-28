from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import Feed, Profile, CreatePost, Like


urlpatterns = [
    path('', Feed.as_view(), name="feed"),
    path('profile/<int:user_id>', login_required(Profile.as_view()), name="profile"),
    path('create_post/', login_required(CreatePost.as_view()), name="create_post"),
    path('like/<int:post_id>', login_required(Like.as_view()), name="like"),
]
