# Generated by Django 4.1.1 on 2022-09-15 02:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_timesheet_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheet',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
