# Generated by Django 4.1.1 on 2022-09-13 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_timesheet_checkin_alter_timesheet_checkout_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='checkout',
            field=models.TimeField(blank=True, null=True, verbose_name='check out'),
        ),
    ]
