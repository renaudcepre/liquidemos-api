# Generated by Django 4.0 on 2022-02-04 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0019_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]
