from django.contrib import admin
from django.contrib.gis.db import models as geo_models
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin, LeafletWidget
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from . import models

@admin.register(models.EventType)
class EventType(admin.ModelAdmin):
    pass

@admin.register(models.Location)
class Location(LeafletGeoAdmin):
    def _get_map_widget(self, db_field, widget):
        widget = super()._get_map_widget(db_field, widget)
        widget.display_raw = True
        return widget

@admin.register(models.DistributionType)
class DistributionType(admin.ModelAdmin):
    fields = (('name', 'abbreviation'), 'has_shape_parameter')

@admin.register(models.StatisticalMethod)
class StatisticalMethod(admin.ModelAdmin):
    pass

@admin.register(models.AttributionVariable)
class AttributionVariable(admin.ModelAdmin):
    fields = (('short_name', 'long_name'), ('unit', 'unit_symbol', 'delta_I_unit_symbol'), 'description') 

@admin.register(models.ObservationDataSet)
class ObservationDataSet(admin.ModelAdmin):
    fields = ('name', 'description', ('url', 'doi'), 'papers') 

@admin.register(models.ModelDataSet)
class ModelDataSet(admin.ModelAdmin):
    fields = ('model_name', 'model_description', 'experiment', 'experiment_description',('url', 'doi'), 'papers') 

@admin.register(models.JournalPaper)
class JournalPaper(admin.ModelAdmin):
    fields = ('title', 'authors', ('journal', 'issue', 'date'), ('url', 'doi')) 

@admin.register(models.PressCommunication)
class PressRelease(admin.ModelAdmin):
    fields = ('title', 'authors', ('medium', 'date'), ('url', 'doi')) 
    pass

from django import forms

def small_inputs():
    return { geo_models.CharField: {'widget': forms.TextInput(attrs={'size':'32'})},
        geo_models.TextField: {'widget': forms.Textarea(attrs={'rows':'3', 'cols':'40'})},
        geo_models.FloatField: {'widget': forms.TextInput(attrs={'size':'6'})},
        geo_models.IntegerField: {'widget': forms.NumberInput(attrs={'style':'width:6ch'})},
        geo_models.PositiveIntegerField: {'widget': forms.NumberInput(attrs={'style':'width:6ch'})},}

class ObservationAnalysisInline(admin.TabularInline):
    model = models.ObservationAnalysis
    fields = (  ('dataset', 'variable_value' ),
                ('y_pres', 'y_past'),
                ('sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max'), 
                ('PR', 'PR_min', 'PR_max'), 
                ('Delta_I', 'Delta_I_min', 'Delta_I_max'),
                ('T_return', 'T_return_min', 'T_return_max'), 
                'comments')
    extra = 0
    inlines = []
    formfield_overrides = small_inputs()

class ModelAnalysisInline(admin.TabularInline):
    model = models.ModelAnalysis
    fields = (  ('dataset' ),
                ('y_pres', 'y_past'),
                ('sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max'), 
                ('PR', 'PR_min', 'PR_max'), 
                ('Delta_I', 'Delta_I_min', 'Delta_I_max'),
                'comments')
    extra = 0
    inlines = []
    formfield_overrides = small_inputs()

class AttributionInline(NestedStackedInline):
    model = models.Attribution
    extra = 0
    fieldsets = ( (None, {'fields': (('description', 'location'),)}),
                  ('Method', {'fields': (('variable', 'distribution', 'statistical_method'),)}),
                  ('Synthesis', {'fields' : ('return_period', ('PR', 'PR_min', 'PR_max'), ('Delta_I', 'Delta_I_min', 'Delta_I_max'), 'conclusions')}),
                  ('Dissemination', {'fields' : ('contact', 'webpage', 'papers', 'press_communication', ('research_data', 'research_data_doi'))}) )
    inlines = [ObservationAnalysisInline, ModelAnalysisInline]


class ImpactResourceInline(NestedStackedInline):
    model = models.ImpactResource
    extra = 0


@admin.register(models.Event)
class Event(LeafletGeoAdminMixin, NestedModelAdmin):
    fieldsets = ( (None, {'fields': ('name', 'event_type', 'image', 'image_caption', 'comments')}), 
                ('Event Definition', {'fields' : (('region','map_location'), ('start_date', 'duration', 'season'))}),
                ('Impact', {'fields' : (('deaths', 'people_affected', 'economical_loss'), ('socio_economic_impact'), ('environmental_impact'))}),
                ('Attribution request', {'fields': ('atrribution_consideration_statement',)}) )
                
    inlines = [
        ImpactResourceInline, AttributionInline,
    ]


    def _get_map_widget(self, db_field, widget):
        widget = super()._get_map_widget(db_field, widget)
        widget.map_height = "200px"
        widget.map_width = "100%"
        return widget

