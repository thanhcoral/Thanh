import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


GROUPS = ['System Admin', 'Sub Admin', 'HR', ]

class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            logging.warning(f"Created group: {group}")
        print("Created default groups.")