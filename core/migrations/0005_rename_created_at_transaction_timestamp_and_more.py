# Generated by Django 4.2.1 on 2023-07-11 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_stripe_payment_intent_id_transaction_paypal_payment_intent_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='created_at',
            new_name='timestamp',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='paypal_customer_id',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='paypal_email',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='paypal_payment_method_id',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='paypal_payment_intent_id',
        ),
        migrations.AddField(
            model_name='transaction',
            name='order_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
