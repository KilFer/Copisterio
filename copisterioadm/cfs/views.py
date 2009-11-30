from django.http import HttpResponse
from django.shortcuts import render_to_response
from copisterioadm.cfs.models import Pending, Processing, Approved
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render_to_response('adm.html', {'pending_list': Pending, 'title': "Administration" })

def count(request):
    return HttpResponse(Pending.objects.all().count, mimetype='text/plain')

