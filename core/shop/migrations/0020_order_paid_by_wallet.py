# Generated by Django 4.2.8 on 2024-08-08 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_customer_wallet_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid_by_wallet',
            field=models.IntegerField(default=0),
        ),
    ]
