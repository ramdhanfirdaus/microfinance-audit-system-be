from django.db import models

# Create your models here.
class AuditCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=15)

class AuditType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=15)