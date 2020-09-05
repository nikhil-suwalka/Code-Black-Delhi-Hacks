from django.db import models


# Create your models here.

class Session(models.Model):
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Question(models.Model):
    question_id = models.IntegerField(blank=False, null=False, unique=True, primary_key=True)
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_link")
    question = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return str(self.question)


class Option(models.Model):
    option_id = models.IntegerField(blank=False, null=False, unique=True, primary_key=True)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_link")

    def __str__(self):
        return str(self.option_id)
