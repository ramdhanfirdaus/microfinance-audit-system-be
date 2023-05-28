from django.db import models
from django.contrib.auth.models import User

from audit import models as audit_models

# Create your models here.

class Auditor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    on_audit = models.BooleanField(default=False, blank=False, null=False)
    session = models.ForeignKey(
        audit_models.AuditSession,
        on_delete = models.CASCADE,
        blank = True,
        null = True,
    )
    list_history = models.TextField(default='[]')

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
