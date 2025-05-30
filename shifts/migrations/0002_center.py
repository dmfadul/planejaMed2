# Generated by Django 5.1.6 on 2025-04-21 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=5)),
                ('hospital', models.CharField(default='Evangélico', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
