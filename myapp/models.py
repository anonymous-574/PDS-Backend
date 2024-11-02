from django.db import models

# Create your models here.
class Input_text(models.Model):
    text = models.CharField(max_length=1000)
    
class Input_image(models.Model):
    image=models.ImageField(upload_to='images/',blank=True)