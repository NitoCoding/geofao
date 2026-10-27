from django.apps import AppConfig


class IamConfig(AppConfig):
    name = 'apps.iam'
    label = 'iam'

    # RBAC Template Configuration
    # Toggle ini untuk mengaktifkan mode multi-role
    # False = single role (default), True = multi-role
    rbac_enable_multi_role = False

    default_password_reset = '' # empty if want regenerated 8 random characters
