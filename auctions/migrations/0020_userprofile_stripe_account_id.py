# Generated by Django 3.2.5 on 2021-08-05 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_buyrequest_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stripe_account_id',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
