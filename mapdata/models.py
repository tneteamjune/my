from django.db import models

# Create your models here.
class MapInfo(models.Model):
    lng = models.FloatField(("lng"))
    lat = models.FloatField(("lat"))
    content = models.CharField("content", max_length=255)    
    title = models.CharField("title", max_length=255)
