# Generated by Django 5.1.1 on 2024-12-15 09:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 15, 10, 50, 10, 152078, tzinfo=datetime.timezone.utc)),
        ),
    ]
