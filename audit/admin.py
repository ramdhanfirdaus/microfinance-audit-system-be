from django.contrib import admin

from.models import AuditType, AuditSession

# Register your models here.
admin.site.register(AuditType)
admin.site.register(AuditSession)