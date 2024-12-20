# Generated by Django 4.2.15 on 2024-11-30 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_product_express'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpressDeliveryInterval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('total_cap', models.IntegerField(default=100)),
                ('teken_cap', models.IntegerField(default=0)),
            ],
        ),
    ]
