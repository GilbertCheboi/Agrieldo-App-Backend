# Generated by Django 5.1.1 on 2025-04-01 07:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0049_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 1, 8, 58, 56, 503815, tzinfo=datetime.timezone.utc)),
        ),
    ]
