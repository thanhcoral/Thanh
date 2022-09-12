from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Unknown', 'Unknown'),
)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_("username"), max_length=100, unique=True, validators=[UnicodeUsernameValidator()], error_messages={"unique": _("A user with that username already exists."),})
    first_name = models.CharField(_("first name"), max_length=100, blank=True)
    last_name = models.CharField(_("last name"), max_length=100, blank=True)    # Surname
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
        if self.last_name == "" and self.first_name == "":
            return self.username
        return f"{self.last_name} {self.first_name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='avatar_default.jpg', upload_to='images')
    gender = models.CharField(_("gender"), max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"