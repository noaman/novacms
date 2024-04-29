from django import template
from django.template.defaultfilters import stringfilter
from backend.models import *
import re

register = template.Library()
from django.template import Template, Context

import requests

from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags



@register.filter()
def showCategoryPageProductBlock(post:BlogPost):
    # data_list = data.split(",")
    return render_to_string("subtemplates/cat_productblock.html", {
        'post': post,
        
    })


