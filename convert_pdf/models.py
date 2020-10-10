from django.db import models


# Create your models here.
class PdfFile(models.Model):
    file_name = models.CharField(max_length=500)
    date = models.DateTimeField("date")
    upload = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.file_name
