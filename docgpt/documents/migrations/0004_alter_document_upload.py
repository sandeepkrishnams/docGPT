# Generated by Django 4.2.4 on 2023-08-18 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_rename_user_name_document_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='upload',
            field=models.FileField(blank=True, null=True, upload_to='%Y/%m/%d/'),
        ),
    ]
