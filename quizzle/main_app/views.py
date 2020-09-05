from django.http import HttpResponse
from django.shortcuts import render
from .models import *
# Create your views here.


def home_view(request):
    if request.session.get("session_id", False):
        s = Session.objects.create()
        request.session["session_id"] = s.session_id
        print(request.session.get("Session created: " + str(s)))

        return HttpResponse("You've newwwww: " +str(s))
    else:
        print(request.session.get("session_id"))
        return render(request,'home.html',{})

