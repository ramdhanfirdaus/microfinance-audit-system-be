from django.contrib import admin

from.models import AuditCategory
from.models import AuditType

# Register your models here.
admin.site.register(AuditCategory)
admin.site.register(AuditType)