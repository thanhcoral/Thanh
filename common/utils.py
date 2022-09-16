import datetime

from django.utils import timezone


def get_time_now():
    datee =datetime.datetime.strptime(str(timezone.now()), "%Y-%m-%d %H:%M:%S.%f")
    year = datee.year
    month = datee.month
    day = datee.day
    return [year, month, day]