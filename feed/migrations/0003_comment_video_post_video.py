# Generated by Django 5.1.2 on 2024-10-17 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0002_alter_post_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='comments/videos/'),
        ),
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='post/videos/'),
        ),
    ]
