from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from .models import Event, Attribution, Region, ObservationDataSet, ModelDataSet
from .forms import EventForm, RegionForm


class Index(ListView):
    template_name = 'exevada/index.html'
    model = Event


class EventsView(ListView):
    template_name = 'exevada/events.html'
    model = Event
    context_object_name = 'events'


class EventView(DetailView):
    template_name = 'exevada/event.html'
    model = Event
    context_object_name = 'event'


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


class ObsDatasets(ListView):
    template_name = 'exevada/obsdatasets.html'
    model = ObservationDataSet


class ModDatasets(ListView):
    template_name = 'exevada/moddatasets.html'
    model = ModelDataset
