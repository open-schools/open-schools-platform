# Generated by Django 3.2.12 on 2022-03-27 09:12

from django.db import migrations, models
import open_schools_platform.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='creationtoken',
            managers=[
                ('objects', open_schools_platform.users.models.CreationTokenManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', open_schools_platform.users.models.UserManager()),
            ],
        ),
        migrations.RenameField(
            model_name='creationtoken',
            old_name='token',
            new_name='key',
        ),
        migrations.AddField(
            model_name='creationtoken',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
