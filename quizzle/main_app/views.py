from django.http import HttpResponse
from django.shortcuts import render
from .models import *


# Create your views here.


def home_view(request):
    print("qwerty", request.session)
    if request.session.get("session_id", False):
        print("Old session exists: ", request.session.get("session_id"))

        return render(request,"home.html",{})


    else:
        s = Session.objects.create()
        request.session["session_id"] = s.id
        print("New session created: ", s.id)

        return render(request,"home.html",{})


def deleteSession(request):
    try:
        del request.session["session_id"]
        request.session.modified = True
        return True
    except:
        return False


def createQuestion(que: str, session_id: int) -> int:
    q = Question.objects.create(session_id=Session.objects.filter(id=session_id).first(), question=que)
    return q.id


def createOption(option_text: str, question_id: int, session_id: int) -> None:
    o = Option.objects.create(session_id=Session.objects.filter(id=session_id).first(),
                              question_id=Question.objects.filter(id=question_id).first(), option=option_text)
