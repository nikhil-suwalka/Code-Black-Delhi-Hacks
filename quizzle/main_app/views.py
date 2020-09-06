from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from .models import *


# Create your views here.


def home_view(request):
    if request.method == "POST":
        print(request.POST)
        session_id = request.session.get("session_id", False)
        if request.POST.get("add_que", False) == "":
            dict1 = {}
            ans = []
            lastque = -1
            for i in request.POST:
                if "option" in i and i[8] == lastque:
                    dict1[list(dict1.keys())[-1]].append(request.POST[i])
                    if "ans" in i:
                        ans.append(request.POST[i])
                elif "question" in i and "option" not in i:
                    dict1[request.POST[i]] = []
                    lastque = i[8]


            i = 0
            for q in dict1:
                que = createQuestion(que=q, ans=ans[i], session_id=session_id)
                i += 1
                for a in dict1[q]:
                    createOption(option_text=a, question_id=que)
            return render(request, "home.html", context={"selected": request.POST.get("selectTextArea"),
                                                         "data": request.POST.get("mainTextArea")})

        elif request.POST.get("export_btn", False) == "":
            print("Export button")
            # print(getQuestionWithOptions(session_id), getQuestionWithAnswers(session_id))
            # file = open("temp.txt", "w")
            # file.write(str(getQuestionWithOptions(session_id)))
            # file.close()
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=temp.txt'
            response.write(str(getQuestionWithOptions(session_id)))
            return response

            # return render(request, "home.html", context={"selected": request.POST.get("selectTextArea"),
            #                                              "data": request.POST.get("mainTextArea")})

        else:
            string = request.POST.get("selectTextArea")
            data = request.POST.get("mainTextArea")
            # questionList = get_questions_list(string)
            questionList = [[
                'The  _______  is a muscular, hollow organ in the gastrointestinal tract of humans and many other animals, including several invertebrates.',
                'Stomach', ['Stomach', 'Intestine', 'Heart', 'Excretory Organ', 'Liver', 'Hindgut'],
                ['Intestine', 'Liver', 'Respiratory Organ', 'Viscera']], [
                'The stomach is a muscular, hollow  _______  in the gastrointestinal tract of humans and many other animals, including several invertebrates.',
                'Organ', ['Organ', 'Ambulacrum', 'Adnexa', 'Abdomen', 'Apparatus', 'Ampulla'],
                ['Ampulla', 'Apparatus', 'Area', 'Back', 'Buttock', 'Buttocks', 'Cannon', 'Dilator',
                 'Dock', 'Dorsum', 'Energid', 'External Body Part', 'Feature', 'Flank', 'Fornix',
                 'Gaskin', 'Groove', 'Haunch', 'Hindquarters', 'Hip', 'Horseback', 'Joint', 'Lobe',
                 'Loin', 'Loins', 'Mentum', 'Partition', 'Process', 'Rectum', 'Rudiment', 'Saddle',
                 'Shank', 'Shin', 'Shoulder', 'Small', 'Structure', 'Stump', 'System', 'Thorax',
                 'Tissue', 'Toe', 'Torso', 'Underpart', 'Venter', 'Withers']], [
                'The stomach is a muscular, hollow organ in the gastrointestinal tract of  _______  and many other animals, including several invertebrates.',
                'Humans', ['Australopithecine', 'Pithecanthropus', 'Homo', 'Humans', 'Javanthropus',
                           'Dryopithecine'],
                ['Javanthropus', 'Pithecanthropus', 'Sinanthropus', 'Sivapithecus']]]
            # questionList = []
            return render(request, "home.html", context={"questions": questionList, "selected": string, "data": data})


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


def createQuestion(que: str, session_id: int, ans: str) -> int:
    q = Question.objects.create(session_id=Session.objects.filter(id=session_id).first(), question=que, answer=ans)
    return q.id


def createOption(option_text: str, question_id: int) -> None:
    o = Option.objects.create(question_id=Question.objects.filter(id=question_id).first(), option=option_text)


def getQuestionWithOptions(session_id:int):
    dict1 = {}
    questions = Question.objects.filter(session_id=session_id)

    for que in questions:

        temp = []
        for option in Option.objects.filter(question_id=que.id):
            temp.append(option.option)
        dict1[que.question] = temp

    return dict1

def getQuestionWithAnswers(session_id:int):
    dict1 = {}
    questions = Question.objects.filter(session_id=session_id)

    for que in questions:
        dict1[que.question] = que.answer
    return dict1
#
# from main_app import generate_questions
#
#
# def get_questions_list(text: str) -> list:
#     return generate_questions.get_questions(text)
