# Generated by Django 4.2.8 on 2024-08-08 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_store_has_notif'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ref_class',
            field=models.CharField(blank=True, default='بدون کلاس', max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='ref_price',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_alarm_volume',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
