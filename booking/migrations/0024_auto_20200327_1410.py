# Generated by Django 3.0.3 on 2020-03-27 06:10

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0023_auto_20200327_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_date', models.DateTimeField(default=datetime.datetime(2020, 3, 27, 14, 10, 14, 847151))),
                ('stars', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='book_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 27, 14, 10, 14, 846123)),
        ),
    ]
