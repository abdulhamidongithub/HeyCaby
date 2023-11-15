# Generated by Django 4.2.7 on 2023-11-13 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0002_remove_drivers_fullname'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('longitude', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.CharField(blank=True, max_length=255, null=True)),
                ('driver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='drivers.drivers')),
            ],
        ),
    ]
