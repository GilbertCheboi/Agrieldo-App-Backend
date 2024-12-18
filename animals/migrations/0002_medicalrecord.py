# Generated by Django 5.1.1 on 2024-09-14 12:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('diagnosis', models.CharField(max_length=255)),
                ('treatment', models.TextField()),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='animals.animal')),
                ('veterinarian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
