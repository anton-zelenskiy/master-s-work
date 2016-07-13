import re
from operator import itemgetter

from entity.models import Entity, LinksBetweenEntities
from nltk import SnowballStemmer


class LinkingEntities:
    def __init__(self, entities, entity):
        self.entities = entities
        self.entity = entity

    def get_entities(self):  # create linked descriptions (on main)
        elements = []
        for item in self.entities:
            # if item.is_linked:
            #     continue
            new_description = self.add_links_to_description3(item.id, item.description)
            element_data = {
                'id': item.id,
                'item_name': item.item_name,
                'description': new_description,
            }
            elements.append(element_data)
        return elements

    def get_entity(self):  # create linked description (on "get" item page)
        # if not self.entity.is_linked:
        new_description = self.add_links_to_description3(self.entity.id, self.entity.description)
        element = {'id': self.entity.id,
                   'item_name': self.entity.item_name,
                   'description': new_description}
        return element

    def get_stemmed_names_of_entity(self):  # get stemmed names of entities
        stemmer = SnowballStemmer('russian')
        stemmed_names_in = self.get_names_of_entity()
        stemmed_names_out = []
        for item in stemmed_names_in:
            stemmed = " ".join([stemmer.stem(word.lower()) for word in item.get('name').split(" ")])  # for чтобы
            # отстеммить name_of_entity, состоящий из нескольких слов
            if stemmed.endswith('ок'):
                stemmed = stemmed[:-2] + 'к'
            stemmed_names_out.append({'stemmed_name': str(stemmed).lower(),
                                      'id': item.get('id')})
        return stemmed_names_out

    def get_names_of_entity(self):  # get all names of entities for project
        descriptions = []
        for item in self.entities:
            descriptions.append({'name': item.item_name, 'id': item.id})
        return descriptions

    def make_footnotes(self, description, current_id):
        stemmer = SnowballStemmer('russian')
        # получить список названий сущностей, отстеммленных и отсортированных по возр.
        stemmed_names_from_entities = self.get_stemmed_names_of_entity()
        sorted_stemmed_names_from_entities = sorted(stemmed_names_from_entities, key=lambda k: len(k['stemmed_name']))
        sorted_stemmed_names_from_entities.reverse()

        description_wp = re.sub(r'[.,:]', '', description)
        stemmed_description = " ".join([stemmer.stem(word.lower()) for word in description_wp.split(" ")])
        # решаем проблему с формой слов, оканчивающихся на 'ок' во множественном числе. мб еще добавим правила
        split = stemmed_description.split(" ")
        spl2 = []
        for s in split:
            if s.endswith('ок'):
                spl2.append(s[:-2] + 'к')
            else:
                spl2.append(s)
        stemmed_description = ' '.join(spl2)

        entity_name_coords = []
        for stem_name in sorted_stemmed_names_from_entities:
            stemmed_name = stem_name.get('stemmed_name')

            for entity_name in re.finditer(stemmed_name, stemmed_description):
                item = (entity_name.start(), entity_name.end() - 1, stem_name.get("id"))
                # проверяем, stem_name попадает в уже найденные координаты? (если нашли совместный доступ к заметке, то
                # не нужно искать в этой фразе слово 'заметке')
                if not entity_name_coords:
                    entity_name_coords.append(item)
                else:
                    for coord in entity_name_coords:
                        if (coord[0] <= item[0] < coord[1]) \
                                and (coord[0] < item[1] <= coord[
                                    1]):  # слово попало в промежуток - нужно отбросить его поиск
                            break
                        else:
                            entity_name_coords.append(item)
                            break

        self.remove_word_in_word(entity_name_coords)  # можно выпилить?

        new_entity_name_coords = []
        while len(new_entity_name_coords) < 2:
            if len(entity_name_coords) == 0:
                break
            for entity in entity_name_coords:
                if entity[2] != current_id:
                    new_entity_name_coords.append(entity)

        stemmed_description_find = [(m.group(0), m.start(), m.end() - 1) for m in
                                    re.finditer(r'\S+', stemmed_description)]

        footnote_dict = []
        # ищем слова в стеммленном описании по координатам:
        for i, coord in enumerate(new_entity_name_coords):
            start_index, end_index = 0, 0
            for index1, elem1 in enumerate(stemmed_description_find):
                if coord[0] == elem1[1]:
                    start_index = index1
                if coord[1] == elem1[2]:
                    end_index = index1

            range_list = range(start_index, end_index + 1)
            last_index = range_list[-1]  # сюда будем вставлять новый description

            footnote_entity = Entity.objects.get(id=coord[2])

            footnote_element = {}
            if i == 0:
                footnote_element['index'] = last_index + 1
            else:
                footnote_element['index'] = last_index + len(footnote_element) + 1

            mod_footnote_entity = '<br> <p style="margin-left: 30px; font-style: italic"> ' + footnote_entity.description + '</p>'
            footnote_element['description'] = mod_footnote_entity
            footnote_dict.append(footnote_element)

        # сортируем footnote_dict, чтобы правильно сформировать сноски (описания встали в нужные места)
        new_footnote_dict = sorted(footnote_dict, key=itemgetter('index'), reverse=True)

        split_description = description.split(" ")
        for item in new_footnote_dict:
            split_description.insert(item.get('index'), item.get('description'))

        description = ' '.join(split_description)

        return description

    def add_links_to_description3(self, current_id, description=''):
        stemmer = SnowballStemmer('russian')
        # получить список названий сущностей, отстеммленных и отсортированных по возр.
        stemmed_names_from_entities = self.get_stemmed_names_of_entity()
        sorted_stemmed_names_from_entities = sorted(stemmed_names_from_entities, key=lambda k: len(k['stemmed_name']))
        sorted_stemmed_names_from_entities.reverse()

        splitted_description = description.split(" ")
        description_wp = re.sub(r'[.,:]', '', description)
        stemmed_description = " ".join([stemmer.stem(word.lower()) for word in description_wp.split(" ")])
        # решаем проблему с формой слов, оканчивающихся на 'ок' во множественном числе. мб еще добавим правила
        split = stemmed_description.split(" ")
        spl2 = []
        for s in split:
            if s.endswith('ок'):
                spl2.append(s[:-2] + 'к')
            else:
                spl2.append(s)
        stemmed_description = ' '.join(spl2)

        entity_name_coords = []
        for stem_name in sorted_stemmed_names_from_entities:
            stemmed_name = stem_name.get('stemmed_name')
            for entity_name in re.finditer(stemmed_name, stemmed_description):
                item = (entity_name.start(), entity_name.end() - 1, stem_name.get("id"))
                # проверяем, stem_name попадает в уже найденные координаты? (если нашли совместный доступ к заметке, то
                # не нужно искать в этой фразе слово 'заметке')
                if not entity_name_coords:
                    entity_name_coords.append(item)
                else:
                    for coord in entity_name_coords:
                        if (coord[0] <= item[0] < coord[1]) \
                                and (coord[0] < item[1] <= coord[
                                    1]):  # слово попало в промежуток - нужно отбросить его поиск
                            break
                        else:
                            entity_name_coords.append(item)
                            break

        self.remove_word_in_word(entity_name_coords)  # можно выпилить?

        stemmed_description_find = [(m.group(0), m.start(), m.end() - 1) for m in
                                    re.finditer(r'\S+', stemmed_description)]

        with_tags = ''
        # ищем слова в стеммленном описании по координатам:
        for coord in entity_name_coords:
            start_index, end_index = 0, 0
            for index1, elem1 in enumerate(stemmed_description_find):
                if coord[0] == elem1[1]:
                    start_index = index1
                if coord[1] == elem1[2]:
                    end_index = index1

            # получаем слова, которые будем заменять по индексам:
            replacing_words = []
            for index in range(start_index, end_index + 1, 1):
                replacing_words.append(splitted_description[index])

            # unmark_entities - не линковать сущность, если is_unmarked=True
            unmark_entity = LinksBetweenEntities.objects.filter(from_entity_id=current_id,
                                                                to_entity_id=coord[2],
                                                                is_unmarked=True)
            if unmark_entity:
                continue
            #

            joined_replacing_words = ' '.join(replacing_words)
            start_tag = '<span><a href="/entity/get/' + str(coord[2]) + '/">'
            end_tag = '</a></span>'
            start_tag_search = '<span><a href="/entity/get/">'
            end_tag_search = '</a></span>'
            m = re.search('%s(.*)%s' % (start_tag_search, end_tag_search), description)
            if m:
                with_tags = m.group(0)

            if joined_replacing_words in with_tags:
                continue
            if joined_replacing_words != '':
                new_replacing_words = start_tag + joined_replacing_words + end_tag
                description = description.replace(joined_replacing_words, new_replacing_words)

        return description

    # удалить координаты слова в слове (заметке - метке, удалить 'метке', если 2 слова в пределах одних координат)
    def remove_word_in_word(self, entity_name_coords):
        for index1, elem1 in enumerate(entity_name_coords):
            for index2, elem2 in enumerate(entity_name_coords):
                if index1 != index2:
                    if elem1[0] < elem2[0] < elem1[1] and elem2[1] <= elem1[1]:  # удалить найденное слово в слове :)
                        entity_name_coords.pop(index2)

    def add_links_between_entities(self, linked_entities):
        for entity in linked_entities:
            digits = re.findall(r"\b\d+\b", entity.get('description'))
            if digits:
                entity_id = entity.get('id')
                # current_entity = Entity.objects.get(id=entity_id)
                for number in digits:  # number - это id сущностей, которые есть в description
                    if int(number) != entity_id:
                        # unmarked_entities
                        unmark_entity = LinksBetweenEntities.objects.filter(from_entity_id=entity_id,
                                                                            to_entity_id=number)
                        if unmark_entity:
                            continue

                        link = LinksBetweenEntities(from_entity_id=entity_id,
                                                    to_entity_id=number,
                                                    is_unmarked=False)
                        link.save()

    # def delete_unused_links(self, linked_entities):
    #     for entity in linked_entities:
    #         current_links_ids = re.findall(r"\b\d+\b", entity.get('description'))
    #         current_links_ids_int = [int(x) for x in current_links_ids]
    #         current_entity_id = entity.get('id')
    #         if current_links_ids:
    #             links_in_db = LinksBetweenEntities.objects.filter(from_entity_id=current_entity_id)
    #             db_ids = []
    #             for link in links_in_db:
    #                 db_ids.append(link.to_entity_id)
    #
    #             for i in db_ids:
    #                 if i not in current_links_ids_int:
    #                     LinksBetweenEntities.objects.filter(
    #                         from_entity_id=current_entity_id,
    #                         to_entity_id=i).delete()
