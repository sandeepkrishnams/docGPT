from django.shortcuts import render
from django.http import HttpResponse


def get_answer(request):
    return HttpResponse('get answer')
