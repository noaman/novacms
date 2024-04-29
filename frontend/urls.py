from django.shortcuts import render

# Create your views here.
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.sitemaps.views import sitemap


from django.contrib.sitemaps import GenericSitemap
# from sitemap import StaticViewSitemap
from django.urls import include, re_path

from django.views.generic.base import TemplateView


urlpatterns = [
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),),
    
    
    re_path(r'^c/(?P<catslug>[-\w]+)/?$', views.showCategoryLanding,name="categorylanding"),
    re_path(r'^c/(?P<catslug>[-\w]+)/(?P<p>\d+)/?$', views.showCategoryLanding,name="categorylanding"),
    # re_path(r'^post/(?P<slug>[\w-]+)/?$', views.showPost,name="post"),
    # re_path(r'^(?P<p>\d+)/?$', views.showIndex, name='index'),
    path('',views.showIndex,name="index"),
    # path('projects',views.showProjects,name="projects"),

]

