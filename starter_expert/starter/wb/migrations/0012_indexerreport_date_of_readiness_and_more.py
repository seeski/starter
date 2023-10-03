# Generated by Django 4.2.4 on 2023-09-29 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0011_indexerreportdata_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexerreport',
            name='date_of_readiness',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='indexerreport',
            name='quick_indexation',
            field=models.BooleanField(default=False),
        ),
    ]