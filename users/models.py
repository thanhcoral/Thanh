import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.utils import get_time_now


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Unknown', 'Unknown'),
)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_("username"), max_length=100, unique=True, validators=[UnicodeUsernameValidator()], error_messages={"unique": _("A user with that username already exists."),})
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(_("staff status"), default=False,)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    # REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        if self.profile.last_name == "" and self.profile.first_name == "":
            return self.username
        return f"{self.profile.last_name} {self.profile.first_name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(_("first name"), max_length=100, blank=True)
    last_name = models.CharField(_("last name"), max_length=100, blank=True)    # Surname
    birthday = models.DateField(_("birthday"), max_length=10, blank=True, null=True)
    gender = models.CharField(_("gender"), max_length=100, blank=True, choices=GENDER_CHOICES)
    age = models.IntegerField(_("age"), blank=True, null=True)
    address = models.CharField(_("address"), max_length=100, blank=True)
    avatar = models.ImageField(default='images/avatar_default.jpg', upload_to='images')
    citizen_identification = models.CharField(_("citizen identification"), max_length=100, blank=True, null=True)
    tax_code = models.CharField(_("tax code"), max_length=100, blank=True, null=True)
    degree = models.CharField(_("degree"), max_length=100, blank=True, null=True)
    certificate = models.CharField(_("certificate"), max_length=100, blank=True, null=True)
    marital_status = models.CharField(_("marital_status"), max_length=100, blank=True, null=True)
    license_plates = models.CharField(_("license_plates"), max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class TimeSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    checkin = models.DateTimeField(_("check in"), default=timezone.now)
    checkout = models.DateTimeField(_("check out"), blank=True, null=True)

    late = models.IntegerField(blank=True, null=True, default=0)
    ot = models.IntegerField(blank=True, null=True, default=0)
    time = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"timesheet of user: {self.user.username} at {self.day}-{self.month}-{self.year}"

    def save(self, *args, **kwargs):
        self.year, self.month, self.day = get_time_now()
        return super().save(*args, **kwargs)


class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    month = models.IntegerField(blank=True, null=True)
    w_time = models.IntegerField(blank=True, null=True)

    salary = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"salary of user: {self.user.username} at month: {self.month}"

    def save(self, *args, **kwarngs):
        tmp, self.month, tmp = get_time_now()
        list = TimeSheet.objects.filter(user=self.user, month=self.month)
        total = 0
        for li in list:
            total += (li.time)
        self.w_time = total
        self.salary = 1.0 * (total/3600/8*500000)
        return super().save(*args, **kwarngs)




