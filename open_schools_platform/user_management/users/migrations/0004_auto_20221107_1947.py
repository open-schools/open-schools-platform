# Generated by Django 3.2.12 on 2022-11-07 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20221029_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='firebasenotificationtoken',
            name='deleted',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='firebasenotificationtoken',
            name='deleted_by_cascade',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]