from django.shortcuts import render
import json
import os
from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
import os

# Create your views here.



@cache_control(max_age=3600)
def showIndex(request):
    context={}
    return render(request,"index.html",context)
