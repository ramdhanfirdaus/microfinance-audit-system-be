from django.db import models
from django.utils import timezone

# Create your models here.

class AuditType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=15)

class AuditSession(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(
        AuditType,
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(default=timezone.now)

class AuditCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=15)
    audit_type = models.ForeignKey(AuditType, on_delete=models.CASCADE)

class AuditQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    audit_category = models.ForeignKey(AuditCategory, on_delete=models.CASCADE)
    query = models.TextField()