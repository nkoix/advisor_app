# Generated by Django 4.1.5 on 2023-04-04 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("advisor_app", "0006_alter_schedule_isapproved"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course", old_name="credits", new_name="credit",
        ),
    ]
