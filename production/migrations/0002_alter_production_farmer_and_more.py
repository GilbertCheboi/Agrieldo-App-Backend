# Generated by Django 5.1.1 on 2024-11-26 11:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='farmer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='production',
            name='production_type',
            field=models.CharField(choices=[('milk', 'Milk'), ('eggs', 'Eggs'), ('wool', 'Wool')], max_length=20),
        ),
        migrations.AlterField(
            model_name='production',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]