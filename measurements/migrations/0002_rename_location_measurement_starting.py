# Generated by Django 4.0.3 on 2022-03-25 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('measurements', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='measurement',
            old_name='location',
            new_name='starting',
        ),
    ]