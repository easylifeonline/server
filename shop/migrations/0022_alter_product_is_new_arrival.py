# Generated by Django 5.0.6 on 2024-06-29 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0021_product_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_new_arrival',
            field=models.BooleanField(default=True),
        ),
    ]
