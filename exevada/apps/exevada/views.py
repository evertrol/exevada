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
    allow_empty = True


class EventsView(ListView):
    template_name = 'exevada/events.html'
    model = Event
    context_object_name = 'events'


class EventView(DetailView):
    template_name = 'exevada/event.html'
    model = Event
    context_object_name = 'event'

class AttributionsView(ListView):
    template_name = 'exevada/attributions.html'
    model = Attribution
    context_object_name = 'attributions'


class AttributionView(DetailView):
    template_name = 'exevada/attribution.html'
    model = Attribution
    context_object_name = 'attribution'


class ObsDatasets(ListView):
    template_name = 'exevada/obsdatasets.html'
    model = ObservationDataSet
    context_object_name = 'observation_datasets'


class ModDatasets(ListView):
    template_name = 'exevada/moddatasets.html'
    model = ModelDataSet
    context_object_name = 'model_datasets'
