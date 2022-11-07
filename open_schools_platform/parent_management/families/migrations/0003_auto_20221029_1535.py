# Generated by Django 3.2.12 on 2022-10-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0002_auto_20220719_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='deleted',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='family',
            name='deleted_by_cascade',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]