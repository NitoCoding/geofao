
from django.db import models
from config import settings
class Profile(models.Model):
    """
    Pisahkan data yang sering update (biodata) dari User table
    untuk performance (User table sering di-join saat auth)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    join_date = models.DateField(null=True, blank=True)

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
