# Generated by Django 4.2.4 on 2023-08-18 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_alter_document_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='file_hash',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]