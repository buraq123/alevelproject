# Generated by Django 3.0.9 on 2020-12-16 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DEMOAPP', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(max_length=100),
        ),
    ]
