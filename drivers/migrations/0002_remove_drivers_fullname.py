# Generated by Django 4.2.7 on 2023-11-02 21:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drivers',
            name='fullname',
        ),
    ]
