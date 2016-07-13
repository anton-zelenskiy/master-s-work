from django import forms
from django.forms import ModelForm
from .models import Entity


class EntityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.fields['project'].empty_label = None

    class Meta:
        model = Entity
        fields = ['item_name', 'description', 'project']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {'item_name': 'Сущность',
                  'description': 'Описание',
                  'project': 'Проект'}
