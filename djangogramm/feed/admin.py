from django.contrib import admin
from .models import Image, Post, Like, Tag, PostTag

admin.site.register(Image)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Tag)
admin.site.register(PostTag)
