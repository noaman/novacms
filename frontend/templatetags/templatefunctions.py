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

