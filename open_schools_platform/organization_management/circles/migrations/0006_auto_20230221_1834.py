# Generated by Django 3.2.12 on 2023-02-21 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0005_auto_20221029_1535_squashed_0006_added_history_records'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circle',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcircle',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcircle',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]