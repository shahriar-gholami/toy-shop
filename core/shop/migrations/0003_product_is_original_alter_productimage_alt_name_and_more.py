# Generated by Django 4.2.8 on 2024-11-11 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_remove_packageorder_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_original',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='alt_name',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='custom_name',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
