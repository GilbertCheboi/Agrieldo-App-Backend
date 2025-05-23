# Generated by Django 5.1.1 on 2025-03-26 09:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0011_remove_financialdetails_breeding_costs_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LactationPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lactation_number', models.IntegerField()),
                ('last_calving_date', models.DateField()),
                ('days_in_milk', models.IntegerField(editable=False)),
                ('is_milking', models.BooleanField(default=True)),
                ('expected_calving_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lactation_periods', to='animals.animal')),
            ],
        ),
        migrations.DeleteModel(
            name='LactationStatus',
        ),
    ]
