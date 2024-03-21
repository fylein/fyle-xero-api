from django.contrib import admin
from .models import ExpenseAttribute, DestinationAttribute, MappingSetting, Mapping

admin.site.register(ExpenseAttribute)
admin.site.register(DestinationAttribute)
admin.site.register(MappingSetting)
admin.site.register(Mapping)
