# Generated by Django 4.1.6 on 2023-02-07 03:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0003_rename_groups_group"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="group",
            name="pet",
        ),
    ]