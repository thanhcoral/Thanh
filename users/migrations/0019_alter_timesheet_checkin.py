# Generated by Django 4.1.1 on 2022-09-14 11:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_timesheet_checkin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='checkin',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 14, 11, 43, 45, 999238), verbose_name='check in'),
        ),
    ]
