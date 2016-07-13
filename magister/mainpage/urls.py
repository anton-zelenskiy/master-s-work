from django.conf.urls import url
import mainpage.views
from .views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='main'),
    url(r'^index/(?P<project_id>\d+)$', IndexView.as_view(), name='index'),
]