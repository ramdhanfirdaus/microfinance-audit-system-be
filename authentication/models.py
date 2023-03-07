from django.db import models
from .validators import *

# Create your models here.
class User(models.model):
    username = models.CharField(max_length=50, blank=False, unique=True, primary_key=True, validators=[])
    password = models.CharField()
