# Generated by Django 3.2.17 on 2023-03-24 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advisor_app', '0002_schedule_isapproved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='isapproved',
            field=models.BooleanField(default=True),
        ),
    ]
