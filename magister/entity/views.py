from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect, render_to_response
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView
from nltk import SnowballStemmer

from entity.make_links import LinkingEntities
from .models import Entity, LinksBetweenEntities
from django.contrib import messages
from .forms import EntityForm
import pymorphy2


class EntityCreate(SuccessMessageMixin, CreateView):
    model = Entity
    form_class = EntityForm
    template_name = "entity_add.html"
    success_url = reverse_lazy("main")
    success_message = "Сущность успешно создана"

    def get_initial(self):
        init = {'project': self.kwargs.get('project_id')}
        if 'name' in self.request.GET:
            morph = pymorphy2.MorphAnalyzer()
            item_name = morph.parse(self.request.GET['name'])[0].normal_form
            init['item_name'] = item_name.title()
        return init


class EntityDelete(DeleteView):
    model = Entity
    template_name = "entity_delete.html"
    success_url = reverse_lazy("main")

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, "Сущность успешно удалена")
        return super(EntityDelete, self).post(request, *args, **kwargs)


def edit_entity(request, item_id):
    args = {}
    args.update(csrf(request))

    entity = Entity.objects.get(id=item_id)

    args['item_name'] = entity.item_name
    entities = Entity.objects.filter(project_id=entity.project)
    linked_entity = LinkingEntities(entities, entity)
    args['linked_entity'] = linked_entity.get_entity()

    if request.method == 'POST':
        description = request.POST.get('description', '')
        description = description.strip()
        data = {'item_name': request.POST.get('item_name', ''),
                'description': description.replace(u'\xa0', ' '),
                'project': entity.project}
        Entity.objects.filter(id=item_id).update(**data)
        return redirect('index', project_id=entity.project_id)

    return render_to_response('edit_entity.html', args)


class EntityGet(DetailView):
    model = Entity
    template_name = 'show_entity.html'

    def get_context_data(self, **kwargs):
        entity = Entity.objects.get(id=self.kwargs['pk'])
        entities = Entity.objects.filter(project_id=entity.project)
        linked_entity = LinkingEntities(entities, entity)
        footnote_entity = linked_entity.make_footnotes(entity.description, entity.id)
        links = entity.links.filter(to_entity__is_unmarked=False)

        context = {'linked_entity': linked_entity.get_entity(),
                   'entity': entity,
                   'entities': entities,
                   'project_id': entity.project_id,
                   'links': links}
        entity.description = footnote_entity
        context['footnote_entity'] = linked_entity.get_entity()
        return context


@csrf_exempt
def mark_as_entity(request):
    args = {'status': 0}
    if request.POST:
        post_project_id = request.POST.get('project_id', '')
        post_entity_name = request.POST.get('entity_name', '')  # to_hovered_word

        # unmarked_entities
        from_entity = request.POST.get('current_entity_id', '')

        stemmer = SnowballStemmer('russian')
        stem_entity = stemmer.stem(post_entity_name)

        entities = Entity.objects.filter(project_id=post_project_id)
        ent = LinkingEntities(entities, None)
        stem_entities = ent.get_stemmed_names_of_entity()
        to_entity = 0
        for ent in stem_entities:
            if stem_entity == ent.get("stemmed_name"):
                to_entity = ent.get("id")

        if from_entity == to_entity:
            pass
        else:
            unmark_entity = LinksBetweenEntities.objects.filter(from_entity_id=from_entity,
                                                                to_entity_id=to_entity)
            if unmark_entity:
                data = {'from_entity_id': from_entity,
                        'to_entity_id': to_entity,
                        'is_unmarked': False}
                unmark_entity.update(**data)
                args['status'] = 1
                messages.add_message(request, messages.SUCCESS, "Слово отмечено как сущность")
            #
            else:  # add new entity
                morph = pymorphy2.MorphAnalyzer()
                new_entity = morph.parse(post_entity_name)[0].normal_form.title()
                args['new_entity'] = new_entity
                args['status'] = 2
                #
                # new_entity = Entity(item_name=post_entity_name, description='', project_id=post_project_id)
                # new_entity.save()
                # args['status'] = 1
    return JsonResponse(args)


@csrf_exempt
def delete_mark(request):
    args = {'status': 0}
    if request.POST:
        from_entity = request.POST.get('current_entity_id', '')
        to_entity = request.POST.get('to_entity', '')
        project_id = request.POST.get('project_id', '')

        stemmer = SnowballStemmer('russian')
        stem_entity = stemmer.stem(to_entity)

        entities = Entity.objects.filter(project_id=project_id)
        ent = LinkingEntities(entities, None)
        stem_entities = ent.get_stemmed_names_of_entity()
        to_id = 0
        for ent in stem_entities:
            if stem_entity == ent.get("stemmed_name"):
                to_id = ent.get("id")

        unmark_entity = LinksBetweenEntities.objects.filter(from_entity_id=from_entity,
                                                            to_entity_id=to_id,
                                                            is_unmarked=False)
        if unmark_entity:
            data = {'from_entity_id': from_entity,
                    'to_entity_id': to_id,
                    'is_unmarked': True}
            unmark_entity.update(**data)
            args['status'] = 1
            messages.add_message(request, messages.SUCCESS, "Связь успешно удалена")

    return JsonResponse(args)
