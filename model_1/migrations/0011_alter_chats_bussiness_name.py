# Generated by Django 5.1.6 on 2025-02-18 07:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_1', '0010_alter_client_bussiness_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chats',
            name='bussiness_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='model_1.bussiness'),
        ),
    ]
