# Generated by Django 3.0.3 on 2020-03-27 05:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0018_auto_20200327_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='over_min',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('No Show', 'No Show'), ('Overstayed', 'Overstayed')], default='Booked', max_length=30),
        ),
        migrations.AlterField(
            model_name='booking',
            name='book_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 27, 13, 29, 28, 337221)),
        ),
    ]
