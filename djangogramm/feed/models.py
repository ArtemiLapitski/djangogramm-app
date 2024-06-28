from django.db.models import Model, ForeignKey, CASCADE, DateTimeField, TextField, CharField, ImageField
from django.contrib.auth import get_user_model
from djangogramm.settings import IMAGE_THUMBNAIL_SIZE
from djangogramm.helpers import image_handler


class Post(Model):
    user = ForeignKey(get_user_model(), on_delete=CASCADE)
    body = TextField(max_length=250)
    datetime_created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body


class Like(Model):
    user = ForeignKey(get_user_model(), on_delete=CASCADE)
    post = ForeignKey(Post, on_delete=CASCADE)
    datetime_created = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Tag(Model):
    tag = CharField(max_length=25, unique=True)

    def __str__(self):
        return self.tag


class PostTag(Model):
    post = ForeignKey(Post, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)
    datetime_created = DateTimeField(auto_now_add=True)


class Image(Model):
    image = ImageField(upload_to="images/")
    post = ForeignKey(Post, on_delete=CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image_handler(path=self.image.path, size=IMAGE_THUMBNAIL_SIZE)
