from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


GROUPS = ['System Admin', 'Sub Admin', 'HR', ]
GROUP_CHOICE = [(g, g) for g in GROUPS]

GROUP_CHOICE = (
    ('Sys Admin', 'Sys Admin'),
    ('Sub Admin', 'Sub Admin'),
    ('HR', 'HR'),
    # (ACCOUNTANT, 'Accountant'),
    # (AR_OFFICER, 'AR Officer'),
    # (AP_OFFICER, 'AP Officer'),
    # (PRODUCTION_MANAGER, 'Production manager'),
    # (PURCHASE_MANAGER, 'Purchase manager'),
    # (STOCK_MANAGER, 'Stock manager'),
    # (SALE_MAN, 'Sale man'),
    ('Inquiries', 'Inquiries'),
)

def group_required(*group_names, login_url=None, raise_exception=False):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        if raise_exception:
            raise PermissionDenied
        return False

    return user_passes_test(in_groups, login_url=login_url)