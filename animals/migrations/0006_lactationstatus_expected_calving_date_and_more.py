# Generated by Django 5.1.1 on 2025-03-05 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0005_alter_lactationstatus_days_in_milk'),
    ]

    operations = [
        migrations.AddField(
            model_name='lactationstatus',
            name='expected_calving_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lactationstatus',
            name='last_calving_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
