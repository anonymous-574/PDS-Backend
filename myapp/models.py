from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Input_text(models.Model):
    text = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
