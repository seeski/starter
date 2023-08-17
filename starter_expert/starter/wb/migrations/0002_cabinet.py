# Generated by Django 4.2.4 on 2023-08-17 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('token', models.TextField()),
            ],
            options={
                'verbose_name': 'Кабинет',
                'verbose_name_plural': 'Кабинеты',
            },
        ),
    ]
