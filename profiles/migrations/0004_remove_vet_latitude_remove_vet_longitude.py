# Generated by Django 5.1.2 on 2024-11-06 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_remove_farmer_role_remove_vet_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vet',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='vet',
            name='longitude',
        ),
    ]
