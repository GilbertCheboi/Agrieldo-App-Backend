# Generated by Django 5.1.1 on 2025-02-28 17:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('role', models.CharField(blank=True, max_length=15, null=True)),
                ('source', models.CharField(choices=[('Campaign', 'Campaign'), ('Referral', 'Referral'), ('Other', 'Other')], default='Campaign', max_length=100)),
                ('referral_name', models.CharField(blank=True, max_length=100, null=True)),
                ('referral_phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('status', models.CharField(choices=[('New', 'New'), ('Contacted', 'Contacted'), ('Converted', 'Converted'), ('Follow-up', 'Follow-up'), ('Interested', 'Interested'), ('Lost', 'Lost')], default='New', max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Farmer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('farm_location', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='farmer_images/')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('second_name', models.CharField(blank=True, max_length=100, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='banner_images/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farmer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('farm_location', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='staff_images/')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('second_name', models.CharField(blank=True, max_length=100, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='staff_banner_images/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15)),
                ('is_available', models.BooleanField(default=True)),
                ('last_active', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vet_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
