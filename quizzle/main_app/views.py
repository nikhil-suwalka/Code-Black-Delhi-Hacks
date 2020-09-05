from django.http import HttpResponse
from django.shortcuts import render
from .models import *


# Create your views here.


def home_view(request):
    print("qwerty", request.session)
    if request.session.get("session_id", False):
        print("Old session exists: ", request.session.get("session_id"))

        return HttpResponse("You're old: " + str(request.session.get("session_id")))


    else:
        s = Session.objects.create()
        request.session["session_id"] = s.id
        print("New session created: ", s.id)

        return HttpResponse("You've newwwww: " + str(s.id))


def deleteSession(request):
    try:
        del request.session["session_id"]
        request.session.modified = True
        return True
    except:
        return False

# def createQuestion(que: str)