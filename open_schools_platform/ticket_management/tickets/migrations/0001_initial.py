# Generated by Django 3.2.12 on 2024-04-11 17:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import rules.contrib.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('queries', '0002_historicalquery'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('query_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='queries.query')),
            ],
            options={
                'abstract': False,
            },
            bases=('queries.query',),
        ),
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('is_sender', models.BooleanField()),
                ('is_seen', models.BooleanField(default=False)),
                ('value', models.CharField(max_length=1400)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket')),
            ],
            options={
                'abstract': False,
            },
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
    ]
