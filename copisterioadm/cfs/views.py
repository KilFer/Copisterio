from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from copisterioadm.cfs.models import Pending, Processing, Approved
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as djangologout

@login_required
def index(request):
    return render_to_response('adm.html', {'pending_list': Pending,
        'title': "Administration" })

def logout(request):
    djangologout(request)
    return render_to_response('adm.html', {'pending_list': Pending, 
        'title': "Administration", 'action': "logout"})

def count(request):
    return HttpResponse(Pending.objects.all().count, mimetype='text/plain')

def doit(request):
    for file in request: 
        if file[1] is "Yes": status=1
        else: status=0
        Pending.objects.add(file[0], status) # FIXME
