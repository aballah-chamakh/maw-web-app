# Generated by Django 4.0 on 2022-12-27 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0007_rename_selected_all_city_selected_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('afex_email', models.EmailField(max_length=254)),
                ('afex_password', models.CharField(max_length=255)),
                ('loxbox_email', models.EmailField(max_length=254)),
                ('loxbox_password', models.CharField(max_length=255)),
                ('mawlety_api_key', models.CharField(max_length=255)),
            ],
        ),
    ]
