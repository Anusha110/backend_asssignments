# Generated by Django 3.0 on 2023-09-09 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='gender',
            field=models.CharField(max_length=50, null=True),
        ),
    ]