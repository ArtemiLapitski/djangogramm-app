# Generated by Django 4.2.10 on 2024-09-13 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('feed', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='like',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.post'),
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='image',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.post'),
        ),
        migrations.AddField(
            model_name='authorfollower',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='authorfollower',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'post')},
        ),
        migrations.AlterUniqueTogether(
            name='authorfollower',
            unique_together={('author', 'follower')},
        ),
    ]