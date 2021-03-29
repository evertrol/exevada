from django.forms import ModelForm
from .models import Event, Region
from .widgets import AreaInput


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = []

class RegionForm(ModelForm):
    class Meta:
        model = Region
        exclude = []
        widgets = {'area': AreaInput()}

