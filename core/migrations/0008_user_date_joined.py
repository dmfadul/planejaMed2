# Generated by Django 5.1.6 on 2025-03-05 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_user_compliant_since'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default='2020-01-01'),
        ),
    ]
