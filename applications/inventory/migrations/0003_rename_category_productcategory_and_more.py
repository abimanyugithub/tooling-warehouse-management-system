# Generated by Django 4.2.16 on 2024-11-28 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_category_producttype_uom_product'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Category',
            new_name='ProductCategory',
        ),
        migrations.RenameModel(
            old_name='UOM',
            new_name='ProductUOM',
        ),
    ]