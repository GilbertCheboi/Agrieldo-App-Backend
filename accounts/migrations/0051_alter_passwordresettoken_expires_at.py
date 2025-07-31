

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0050_alter_passwordresettoken_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',

            field=models.DateTimeField(default=datetime.datetime(2025, 7, 21, 11, 11, 21, 252335, tzinfo=datetime.timezone.utc)),

        ),
    ]
