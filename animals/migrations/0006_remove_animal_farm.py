# Generated by Django 5.1.2 on 2024-10-15 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0005_animal_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animal',
            name='farm',
        ),
    ]