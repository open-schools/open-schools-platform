# Generated by Django 3.2.12 on 2024-03-25 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketcomment',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ticketcomment',
            name='is_sender',
            field=models.BooleanField(),
        ),
    ]
