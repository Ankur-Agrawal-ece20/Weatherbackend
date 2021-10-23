from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Location(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE,related_name='member1',null=True,blank=True)
    lat=models.FloatField()
    long=models.FloatField()
    city=models.CharField(max_length=500)
    rainfallalert=models.BooleanField(default=True)
    def __str__(self):
        return self.city