# Generated by Django 5.1.1 on 2025-03-12 07:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_force_remove_latlong'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 12, 8, 51, 58, 155531, tzinfo=datetime.timezone.utc)),
        ),
    ]
