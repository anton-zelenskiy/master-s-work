from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Project
from django.contrib import messages
from .forms import ProjectAddForm


class ProjectCreate(SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectAddForm
    template_name = "project_add.html"
    success_url = reverse_lazy("main")
    success_message = "Проект успешно создан"


class ProjectUpdate(SuccessMessageMixin, UpdateView):
    model = Project
    form_class = ProjectAddForm
    template_name = "project_edit.html"
    success_url = reverse_lazy("main")
    success_message = "Проект успешно изменен"


class ProjectDelete(DeleteView):
    model = Project
    template_name = "project_delete.html"
    success_url = reverse_lazy("main")

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, "Проект успешно удален")
        return super(ProjectDelete, self).post(request, *args, **kwargs)
