from django.db import models


class Project(models.Model):
    project_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.project_name
