from django import forms
from django.forms import ModelForm
from .models import Project


class ProjectAddForm(ModelForm):
    class Meta:
        model = Project
        fields = ('project_name', )
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {'project_name': "Проект"}
