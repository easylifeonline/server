# Generated by Django 5.0.6 on 2024-06-28 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_product_created_at_product_is_best_seller_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
