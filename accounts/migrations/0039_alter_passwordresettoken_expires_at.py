# Generated by Django 5.1.1 on 2024-12-26 09:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0038_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 26, 10, 26, 27, 779174, tzinfo=datetime.timezone.utc)),
        ),
    ]
