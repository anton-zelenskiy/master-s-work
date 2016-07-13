import json
import re

from entity.make_graph import JsonData
from entity.make_links import LinkingEntities
from entity.models import Entity
from project.models import Project
from django.views.generic import TemplateView
from generic.mixins import UrlMixin


class IndexView(TemplateView, UrlMixin):
    template_name = 'projectComponents.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        project_id = 0
        if 'project_id' in self.kwargs:
            project_id = self.kwargs['project_id']
        else:
            project_id = Project.objects.all()[:1].get().id
        entities = Entity.objects.filter(project_id=project_id)
        context['entities'] = entities
        context['projects'] = Project.objects.all()
        context['project_id'] = project_id

        ent = LinkingEntities(entities, None)
        context['linked_entities'] = ent.get_entities()
        ent.add_links_between_entities(context['linked_entities'])
        # ent.delete_unused_links(context['linked_entities'])

        json_data = JsonData().get_json_entities(entities, project_id)
        context['json_data'] = json.dumps(json_data)
        return context
