# Generated by Django 5.1.1 on 2025-03-27 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0013_feedplan'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FeedPlan',
        ),
        migrations.AlterField(
            model_name='feedmanagement',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
