# Generated by Django 5.1.1 on 2024-12-25 09:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 25, 10, 56, 38, 747678, tzinfo=datetime.timezone.utc)),
        ),
    ]
