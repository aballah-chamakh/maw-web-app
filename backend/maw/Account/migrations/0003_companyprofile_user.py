# Generated by Django 4.0 on 2023-10-16 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0002_companyprofile_companywebsitestate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Account.user'),
        ),
    ]
