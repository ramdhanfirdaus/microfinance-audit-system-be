from djongo import models

# Create your models here.
class Coba(models.Model):
    name = models.CharField(max_length=100)