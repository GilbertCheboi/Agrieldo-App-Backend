# Generated by Django 5.1.1 on 2025-03-05 11:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 5, 12, 12, 57, 156693, tzinfo=datetime.timezone.utc)),
        ),
    ]
