# Generated by Django 4.2.4 on 2023-08-11 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_table'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]