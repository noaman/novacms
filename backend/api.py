
from .models import *


def getCategories():
    res = BlogCategory.objects.all()
    return res


def getPages():
    res = Page.objects.all()
    return res

