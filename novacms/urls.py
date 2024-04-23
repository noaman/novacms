from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings
from django.urls import include,path

from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from django.conf.urls import (
handler400, handler403, handler404, handler500
)
from django.views.static import serve





# Add `sitemaps` dictionary:
sitemaps = {
    
}

app_name = 'NovaCMS'


urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^static/(?:.*)$', serve, {'document_root': settings.STATIC_ROOT, }),

# path(
#     "sitemap.xml",
#     sitemap,
#     {"sitemaps": sitemaps},
#     name="django.contrib.sitemaps.views.sitemap",
# ),

path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404 = 'frontend.views.handler404'
# handler500 = 'frontend.views.handler500'
# handler403 = 'frontend.views.handler404'
# handler400 = 'frontend.views.handler404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




