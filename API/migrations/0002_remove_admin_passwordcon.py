# Generated by Django 4.2.3 on 2023-07-12 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='passwordCon',
        ),
    ]
