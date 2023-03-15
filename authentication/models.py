from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Auditor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    on_audit = models.BooleanField(default=False, blank=False, null=False)
