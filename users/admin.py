from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from . import models


class UserAdmin(UserAdmin):
    # fields = ('username', 'password', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff', 'user_permissions', 'groups', )
    fieldsets = (
        (None, {
            # 'fields': ('username', 'password', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff', 'user_permissions', 'groups', )
            'fields': ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'groups')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('user_permissions', 'is_active', 'is_superuser', )
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', )
    list_filter = ('is_staff', 'is_active', )
    search_fields = ('last_name__startswith', )

    class Meta:
        ordering = ('last_name', 'first_name', 'date_joined', )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile)
admin.site.register(models.TimeSheet)
