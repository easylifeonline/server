# Generated by Django 5.0.6 on 2024-06-25 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_visit_clickedproduct_searchquery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='click_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
