# Generated by Django 5.1.6 on 2025-02-17 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_1', '0006_rename_bussniess_name_bussiness_bussiness_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_number', models.CharField(max_length=20)),
                ('bussiness_name', models.CharField(max_length=30)),
            ],
        ),
    ]
