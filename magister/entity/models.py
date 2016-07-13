from django.db import models
from project.models import Project


class Entity(models.Model):
    item_name = models.CharField(max_length=150)
    description = models.CharField(max_length=1024)
    project = models.ForeignKey(Project, default=1)
    links = models.ManyToManyField('self', through='LinksBetweenEntities', symmetrical=False)

    def __str__(self):
        return self.item_name


class LinksBetweenEntities(models.Model):
    from_entity = models.ForeignKey(Entity, related_name='from_entity')
    to_entity = models.ForeignKey(Entity, related_name='to_entity')
    is_unmarked = models.BooleanField(default=0)
