# Generated by Django 5.1.1 on 2025-03-13 07:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 13, 8, 23, 15, 914519, tzinfo=datetime.timezone.utc)),
        ),
    ]
