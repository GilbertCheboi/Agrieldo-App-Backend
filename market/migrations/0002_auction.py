# Generated by Django 5.1.1 on 2024-09-18 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('auction_end_date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(max_length=255)),
            ],
        ),
    ]