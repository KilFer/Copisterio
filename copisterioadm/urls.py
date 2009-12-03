from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^doit/', 'copisterioadm.cfs.views.doit'),
    (r'^accounts/logout/', 'copisterioadm.cfs.views.logout'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'media', 'show_indexes': True}),
    (r'^$', 'copisterioadm.cfs.views.index'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login')
)
