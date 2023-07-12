# Generated by Django 4.2.1 on 2023-07-10 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_pickuped_at_job_pickedup_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='stripe_payment_intent_id',
            new_name='paypal_payment_intent_id',
        ),
        migrations.AddField(
            model_name='transaction',
            name='courier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.courier'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.customer'),
            preserve_default=False,
        ),
    ]