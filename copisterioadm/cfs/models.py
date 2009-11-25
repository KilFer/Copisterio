from django.db import models

# Ok thing is:
# The daemon moves files to admin, creates thumbs and adds them to pending
# Then we process them, put them in state processing (status 1 or 0) and the daemon
# moves/deletes them.
# If moved, daemon will create an entry in Approved (and delete it from processing)
# With the filename and the full path location

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

