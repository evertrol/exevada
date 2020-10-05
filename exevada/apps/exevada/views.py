from django.shortcuts import render
from django.urls import reverse_lazy
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.gis import geos
from .models import Event, EventType, Attribution, ObservationDataSet, ModelDataSet, Location
from project.settings.local import WORDPRESS
import json

class Index(ListView):
    template_name = 'exevada/index.html'
    model = Event
    allow_empty = True
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wp_integrate'] = WORDPRESS
        return context

class EventsView(ListView):
    template_name = 'exevada/events.html'
    model = Event
    context_object_name = 'events'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evttypes = {e.pk: {"name": e.name, "icon": e.icon.url if e.icon else ""} for e in EventType.objects.all()}
        context["evttypes"] = evttypes
        context["event_types"] = json.dumps(evttypes)
        geom = serialize('geojson', Event.objects.all(),
                        geometry_field="map_location",
                        fields=('name','comments','event_type','start_date','pk'))
        context['location_geojson'] = geom
        context['wp_integrate'] = WORDPRESS
        return context

class EventView(DetailView):
    template_name = 'exevada/event.html'
    model = Event
    context_object_name = 'event'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wp_integrate'] = WORDPRESS
        return context

class AttributionsView(ListView):
    template_name = 'exevada/attributions.html'
    model = Attribution
    context_object_name = 'attributions'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        geom = serialize('geojson', Location.objects.all(),
                    geometry_field='area',
                    fields=('name','description',))
        context['location_geojson'] = geom
        context['wp_integrate'] = WORDPRESS
        context['locations'] = [l.name for l in Location.objects.all()]
        return context


class AttributionView(DetailView):
    template_name = 'exevada/attribution.html'
    model = Attribution
    context_object_name = 'attribution'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wp_integrate'] = WORDPRESS
        return context


class ObsDatasets(ListView):
    template_name = 'exevada/obsdatasets.html'
    model = ObservationDataSet
    context_object_name = 'observation_datasets'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wp_integrate'] = WORDPRESS
        return context


class ModDatasets(ListView):
    template_name = 'exevada/moddatasets.html'
    model = ModelDataSet
    context_object_name = 'model_datasets'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wp_integrate'] = WORDPRESS
        return context
