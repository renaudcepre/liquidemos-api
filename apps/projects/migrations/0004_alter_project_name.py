# Generated by Django 4.0 on 2021-12-13 09:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_project_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=64, validators=[django.core.validators.RegexValidator('[a-zA-Z0-9/-_]*')]),
        ),
    ]
