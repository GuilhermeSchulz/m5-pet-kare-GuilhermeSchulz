# Generated by Django 4.1.6 on 2023-02-07 02:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("traits", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="traits",
            old_name="pets",
            new_name="pet",
        ),
    ]