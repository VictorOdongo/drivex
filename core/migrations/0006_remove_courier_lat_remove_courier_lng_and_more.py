# Generated by Django 4.2.1 on 2023-07-12 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_created_at_transaction_timestamp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courier',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='courier',
            name='lng',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_id',
        ),
    ]
