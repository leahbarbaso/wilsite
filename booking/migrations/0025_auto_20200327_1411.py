# Generated by Django 3.0.3 on 2020-03-27 06:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0024_auto_20200327_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='book_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 27, 14, 11, 33, 470224)),
        ),
        migrations.AlterField(
            model_name='review',
            name='submit_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 27, 14, 11, 33, 470224)),
        ),
    ]
