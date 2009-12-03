from django.db import models

class Pending(models.Model):
    thumbs = models.CharField(max_length=3000)
    filename = models.CharField(max_length=3000)

    def __unicode__(self):
        return self.filename
    
    def thumbs(self):
        return self.thumbs.split(",")

class Processing(models.Model):
    status = models.IntegerField()
    filename = models.CharField(max_length=3000)

    def __unicode__(self):
        return self.filename

    def is_rejected(self):
        return self.status

class Approved(models.Model):
    filename = models.CharField(max_length=3000)
    location = models.CharField(max_length=3000) # FUll path

    def __unicode__(self):
        return self.filename

    def location(self):
        return self.location

