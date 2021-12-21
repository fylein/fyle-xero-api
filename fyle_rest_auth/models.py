from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthToken(models.Model):
    """
    Fyle auth tokens
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, help_text='User table relation')
    refresh_token = models.TextField(help_text='Fyle refresh token')

    class Meta:
        db_table = 'auth_tokens'
