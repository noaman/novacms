
from .models import *
from django.core import serializers


def getCategories(catslug=""):

    filter={}
    if(catslug != ""):
        filter = {"slug":catslug}
        res = BlogCategory.objects.filter(**filter).order_by('id')
    else:
        res = BlogCategory.objects.filter(**filter).order_by('id')

    return res


def getPostForCategory(catslug=""):
    category = getCategories(catslug=catslug)

    blogposts = BlogPost.objects.filter(category=category[0]).order_by('id').all()

    

    return {"category":category[0],"blogposts":blogposts}
    



def getPages():
    res = Page.objects.all()
    return res

