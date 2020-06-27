from django.shortcuts import render
from django.urls import reverse_lazy
from django.core.serializers import serialize
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.gis import geos
from .models import Event, Attribution, ObservationDataSet, ModelDataSet, Location


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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        geom = serialize('geojson', Location.objects.all(),
                    geometry_field='area',
                    fields=('name','description',))
        # Add in a QuerySet of all the books
        #geom = geos.GeometryCollection()
        #for attribution in self.object_list:
        #    geom.append(attribution.location.area)
        context['location_geojson'] = geom
        return context



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
