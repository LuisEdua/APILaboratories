# Generated by Django 4.2.3 on 2023-07-14 02:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0008_alter_measures_dispositive_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='manager',
            old_name='phones_number',
            new_name='phone',
        ),
    ]
