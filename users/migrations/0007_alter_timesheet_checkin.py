# Generated by Django 4.1.1 on 2022-09-13 09:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_timesheet_checkin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='checkin',
            field=models.TimeField(default=django.utils.timezone.now, verbose_name='check in'),
        ),
    ]
