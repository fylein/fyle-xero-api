"""
Registering models in Django Admin
"""
from django.contrib import admin

from .models import AuthToken


admin.site.register(AuthToken)
