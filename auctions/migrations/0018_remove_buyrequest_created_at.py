# Generated by Django 3.2.5 on 2021-08-03 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_buyrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyrequest',
            name='created_at',
        ),
    ]
