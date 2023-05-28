from django.contrib import admin

from.models import AuditType, AuditSession, AuditCategory, AuditQuestion, AuditHistory

# Register your models here.
admin.site.register(AuditType)
admin.site.register(AuditSession)
admin.site.register(AuditCategory)
admin.site.register(AuditQuestion)
admin.site.register(AuditHistory)