# Generated by Django 5.1.1 on 2025-03-10 10:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 10, 11, 57, 20, 336701, tzinfo=datetime.timezone.utc)),
        ),
    ]
