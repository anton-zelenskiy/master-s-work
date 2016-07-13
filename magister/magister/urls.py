from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('mainpage.urls')),
    url(r'^project/', include('project.urls')),
    url(r'^entity/', include('entity.urls')),
]