# Generated by Django 4.1.7 on 2023-04-15 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advisor_app', '0010_advisor_email_student_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='advisors',
        ),
        migrations.AddField(
            model_name='student',
            name='advisors',
            field=models.ManyToManyField(to='advisor_app.advisor'),
        ),
    ]
