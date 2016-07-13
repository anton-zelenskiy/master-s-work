from django.conf.urls import url
from .views import EntityCreate, EntityDelete, edit_entity, EntityGet, mark_as_entity, delete_mark

urlpatterns = [
    url(r'^add/(?P<project_id>\d+)/$', EntityCreate.as_view(), name='add_entity'),
    url(r'^(?P<item_id>\d+)/edit/$', edit_entity, name='edit_entity'),
    url(r'^(?P<pk>\d+)/delete/$', EntityDelete.as_view(), name='delete_entity'),
    url(r'^get/(?P<pk>\d+)/$', EntityGet.as_view(), name='get_entity'),
    url(r'^mark/$', mark_as_entity, name='mark'),
    url(r'^delete_mark/$', delete_mark, name='delete_mark'),
]
