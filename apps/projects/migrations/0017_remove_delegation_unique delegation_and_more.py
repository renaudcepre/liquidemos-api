# Generated by Django 4.0 on 2022-01-31 11:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0016_rename_tags_delegation_tag'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='delegation',
            name='unique delegation',
        ),
        migrations.AddConstraint(
            model_name='delegation',
            constraint=models.UniqueConstraint(fields=('delegate', 'delegator', 'tag'), name='unique delegation'),
        ),
    ]
