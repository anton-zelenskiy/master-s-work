from entity.models import Entity, LinksBetweenEntities
from random import randint


class JsonData:

    def get_json_entities(self, entities, project_id):
        data = []
        color_array = ['#30D5C8', '#F0DC82', '#D565B7', '#D66D65', '#77F2D5', '#BB81EB', '#EB8381', '#F5AE51']
        nodes = []
        edges = []
        descriptions = {}
        for entity in entities:
            color_index = randint(0, 7)
            node_object = {'id': entity.id,
                           'label': entity.item_name,
                           'color': {'background': color_array[color_index],
                                     'border': '#713E7F',
                                     'highlight': {'background': 'rgba(97,195,238,0.5)',
                                                   'border': 'black'}},
                           'title': entity.description}
            for link in LinksBetweenEntities.objects.filter(from_entity_id=entity.id):
                link_object = {'from': link.from_entity_id,
                               'to': link.to_entity_id,
                               'dashes': 'true'}
                edges.append(link_object)

            nodes.append(node_object)
            descriptions.update({entity.id: entity.description})
        # удалить повторные 14-2  2-14 связи:
        for i, edge1 in enumerate(edges):
            for j, edge2 in enumerate(edges):
                if edge1.get('from') == edge2.get('to') and edge1.get('to') == edge2.get('from'):
                    edges.pop(i)
        data.append(nodes)
        data.append(edges)
        data.append(descriptions)
        return data