

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',

            field=models.DateTimeField(default=datetime.datetime(2025, 6, 30, 11, 8, 24, 218080, tzinfo=datetime.timezone.utc)),

        ),
    ]
