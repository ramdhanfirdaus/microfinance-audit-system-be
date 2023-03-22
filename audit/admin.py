from django.contrib import admin

from.models import AuditCategory, AuditType, AuditSession

# Register your models here.
admin.site.register(AuditCategory)
admin.site.register(AuditType)
admin.site.register(AuditSession)