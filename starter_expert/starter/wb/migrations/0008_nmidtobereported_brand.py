# Generated by Django 4.2.4 on 2023-09-21 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0007_alter_indexerreportdata_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='nmidtobereported',
            name='brand',
            field=models.CharField(default='', max_length=255),
        ),
    ]
