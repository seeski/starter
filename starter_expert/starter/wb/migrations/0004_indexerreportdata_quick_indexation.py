# Generated by Django 4.2.4 on 2023-10-26 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0003_indexerreportdata_prom'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexerreportdata',
            name='quick_indexation',
            field=models.BooleanField(default=False),
        ),
    ]