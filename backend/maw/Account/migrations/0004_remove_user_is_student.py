# Generated by Django 4.0 on 2023-10-17 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0003_companyprofile_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_student',
        ),
    ]
