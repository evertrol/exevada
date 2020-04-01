from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from .models import Event, ObsDataset, ModelDataset, Region
from .forms import EventForm, RegionForm, ObsDatasetForm, ModelDatasetForm


class Index(ListView):
    template_name = 'exevada/index.html'
    model = Event


class Events(ListView):
    template_name = 'exevada/events.html'
    model = Event
    context_object_name = 'events'


class Event(DetailView):
    template_name = 'exevada/event.html'
    model = Event
    context_object_name = 'event'


class ObsDatasets(ListView):
    template_name = 'exevada/obsdatasets.html'
    model = ObsDataset
    context_object_name = 'datasets'


class ObsDataset(ListView):
    template_name = 'exevada/obsdataset.html'
    model = ObsDataset


class ModelDatasets(ListView):
    template_name = 'exevada/modeldatasets.html'
    model = ModelDataset
    context_object_name = 'datasets'


class ModelDataset(ListView):
    template_name = 'exevada/modeldataset.html'
    model = ModelDataset

class CreateEvent(CreateView):
    template_name = 'exevada/add_event.html'
    form_class = EventForm


class Regions(ListView):
    template_name = 'exevada/regions.html'
    model = Region
    context_object_name = 'regions'


class Region(DetailView):
    template_name = 'exevada/region.html'
    model = Region
    context_object_name = 'region'


class CreateRegion(CreateView):
    template_name = 'exevada/add_region.html'
    form_class = RegionForm
    success_url = reverse_lazy('exevada:regions')
