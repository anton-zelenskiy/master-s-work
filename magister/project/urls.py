from django.conf.urls import url
from .views import ProjectCreate, ProjectUpdate, ProjectDelete

urlpatterns = [
    url(r'^add/$', ProjectCreate.as_view(), name='project_add'),
    url(r'^(?P<pk>\d+)/edit/$', ProjectUpdate.as_view(), name='project_edit'),
    url(r'^(?P<pk>\d+)/delete/$', ProjectDelete.as_view(), name='project_delete'),
]
