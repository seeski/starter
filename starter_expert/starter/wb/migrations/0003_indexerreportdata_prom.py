# Generated by Django 4.2.4 on 2023-10-23 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0002_rename_product_name_indexerreport_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexerreportdata',
            name='prom',
            field=models.CharField(default=None, null=True),
        ),
    ]