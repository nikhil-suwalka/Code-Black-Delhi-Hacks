from django.http import HttpResponse
from django.shortcuts import render
from .models import *


# Create your views here.


def home_view(request):

    if request.method == "POST":
        print("Form submitted")
        string = request.POST.get("selectTextArea")
        data = request.POST.get("mainTextArea")
        questionList = get_questions_list(string)
        print(questionList)
        # questionList = []
        return render(request, "home.html", context={"questions": questionList, "selected": string, "data":data})


    else:
        if request.session.get("session_id", False):
            print("Old session exists: ", request.session.get("session_id"))

            return render(request, "home.html", {})


        else:
            s = Session.objects.create()
            request.session["session_id"] = s.id
            print("New session created: ", s.id)

            return render(request, "home.html", {})


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

#
from main_app import generate_questions
#
#
def get_questions_list(text: str) -> list:
    return generate_questions.get_questions(text)
