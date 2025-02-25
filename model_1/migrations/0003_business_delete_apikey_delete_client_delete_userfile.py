# Generated by Django 5.1.6 on 2025-02-15 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_1', '0002_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(help_text='The model used by the business.', max_length=100)),
                ('file', models.FileField(help_text='File associated with the business.', upload_to='business_files/')),
                ('api', models.CharField(help_text='The API key used by the business.', max_length=255)),
            ],
            options={
                'ordering': ['model'],
            },
        ),
        migrations.DeleteModel(
            name='APIKey',
        ),
        migrations.DeleteModel(
            name='Client',
        ),
        migrations.DeleteModel(
            name='UserFile',
        ),
    ]
