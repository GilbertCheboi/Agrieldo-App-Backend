# Generated by Django 5.1.1 on 2024-12-14 12:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 14, 13, 39, 14, 445381, tzinfo=datetime.timezone.utc)),
        ),
    ]