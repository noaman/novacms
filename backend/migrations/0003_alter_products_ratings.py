# Generated by Django 4.2.11 on 2024-04-22 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_page_alter_products_ratings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='ratings',
            field=models.PositiveIntegerField(default=240),
        ),
    ]