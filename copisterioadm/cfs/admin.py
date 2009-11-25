from django.contrib import admin
from copisterioadm.cfs.models import *

admin.site.register(Pending)
admin.site.register(Processing)
admin.site.register(Approved)

