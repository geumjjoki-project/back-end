# Generated by Django 4.2.20 on 2025-05-22 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0005_rename_reward_mileage_challenge_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchallenge',
            name='end_date',
            field=models.DateTimeField(default='2025-05-22'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userchallenge',
            name='start_date',
            field=models.DateTimeField(default='2025-05-22'),
            preserve_default=False,
        ),
    ]
