from django.forms import ModelForm
from .models import Event, Region, ObsDataset, ModelDataset
from .widgets import AreaInput


class EventForm(ModelForm):
    class Meta:
        model = Event
        #fields = ['name', 'startdate', 'duration', 'variable',
        #          'fitted_distribution']
        exclude = []


class RegionForm(ModelForm):
    class Meta:
        model = Region
        exclude = []
        widgets = {'area': AreaInput()}


class ObsDatasetForm(ModelForm):
    class Meta:
        model = ObsDataset
        exclude = []


class ModelDatasetForm(ModelForm):
    class Meta:
        model = ModelDataset
        exclude = []
