from django.shortcuts import render
import json
import os
from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
import os
from backend.api import *
# Create your views here.



@cache_control(max_age=3600)
def showIndex(request):
    context={}
    return render(request,"index.html",context)


def showCategoryLanding(request,catslug,p="1"):
    posts_data = getPostForCategory(catslug=catslug)

    context={"data":posts_data}
    return render(request,"category.html",context)