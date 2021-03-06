# Generated by Django 4.0 on 2022-01-17 12:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_auto_20211130_1235'),
        ('projects', '0014_delegation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delegation',
            name='delegate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_delegations',
                                    to='users.user'),
        ),
        migrations.AlterField(
            model_name='delegation',
            name='delegator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_delegations',
                                    to='users.user'),
        ),
        migrations.RemoveField(
            model_name='delegation',
            name='tags',
        ),
        migrations.AddField(
            model_name='delegation',
            name='tags',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='projects.tag'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='delegation',
            constraint=models.UniqueConstraint(fields=('delegate', 'delegator'), name='unique delegation'),
        ),
    ]
