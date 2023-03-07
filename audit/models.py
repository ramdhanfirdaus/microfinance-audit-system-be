from django.db import models

# Create your models here.
class AuditCategory(models.Model):
    label = models.CharField(max_length=15)

class AuditType(models.Model):
    label = models.CharField(max_length=15)