# Generated by Django 4.0 on 2022-01-10 11:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0011_alter_project_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ConcurrencyGroup',
            new_name='AlternativeGroup',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='concurrency_group',
            new_name='alternative_group',
        ),
    ]
