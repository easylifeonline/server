# Generated by Django 5.0.6 on 2024-07-02 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_contactsubmission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
