from django.db import models


# Create your models here.
class File(models.Model):
    file_name = models.CharField(max_length=500)
    date = models.DateTimeField('date')
