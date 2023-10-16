# Generated by Django 4.2.6 on 2023-10-16 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0002_rename_cartype_carcategory_driver'),
        ('operators', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sum', models.PositiveIntegerField(default=0)),
                ('finished', models.BooleanField(default=False)),
                ('baggage', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('for_women', models.BooleanField(default=False)),
                ('starting_point_long', models.CharField(max_length=50)),
                ('starting_point_lat', models.CharField(max_length=50)),
                ('destination_long', models.CharField(max_length=50)),
                ('destination_lat', models.CharField(max_length=50)),
                ('cancelled', models.BooleanField(default=False)),
                ('grading_point', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('waiting_seconds', models.PositiveSmallIntegerField(default=0)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='operators.client')),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='drivers.driver')),
            ],
        ),
    ]
