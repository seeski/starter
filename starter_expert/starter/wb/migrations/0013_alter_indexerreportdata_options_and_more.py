# Generated by Django 4.2.4 on 2023-10-06 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0012_indexerreport_date_of_readiness_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indexerreportdata',
            options={'verbose_name': 'Данные по отчету Индексация', 'verbose_name_plural': 'Данные по отчетам Индексация'},
        ),
        migrations.AlterModelOptions(
            name='seocollectorphrasedata',
            options={'verbose_name': 'Данные по отчету Сео', 'verbose_name_plural': 'Данные по отчетам Сео'},
        ),
        migrations.AddField(
            model_name='indexerreport',
            name='product_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]