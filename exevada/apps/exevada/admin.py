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

class ObservationAnalysisInline(NestedStackedInline):
    model = models.ObservationAnalysis
    fields = (  ('dataset', 'variable_value', 'trend' ),
                ('y_pres', 'y_past'),
                ('sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max'), 
                ('PR', 'PR_min', 'PR_max'), 
                ('Delta_I', 'Delta_I_min', 'Delta_I_max'),
                ('T_return', 'T_return_min', 'T_return_max'), 
                'comments')
    extra = 1

class ModelAnalysisInline(NestedStackedInline):
    model = models.ModelAnalysis
    fields = (  ('dataset', 'trend' ),
                ('y_pres', 'y_past'),
                ('sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max'), 
                ('PR', 'PR_min', 'PR_max'), 
                ('Delta_I', 'Delta_I_min', 'Delta_I_max'),
                ('seasonal_cycle', 'spatial_pattern'), 
                'comments')
    extra = 1

class AttributionInline(NestedStackedInline):
    model = models.Attribution
    extra = 1
    fieldsets = ( (None, {'fields': (('description', 'location'),)}),
                  ('Method', {'fields': (('variable', 'distribution', 'statistical_method'),)}),
                  ('Synthesis', {'fields' : ('return_period', ('PR', 'PR_min', 'PR_max'), ('Delta_I', 'Delta_I_min', 'Delta_I_max'), 'conclusions')}),
                  ('Dissemination', {'fields' : ('contact', 'webpage', 'papers', 'press_communication')}) )
    inlines = [ObservationAnalysisInline, ModelAnalysisInline]


@admin.register(models.Event)
class Event(LeafletGeoAdminMixin, NestedModelAdmin):
    fieldsets = ( (None, {'fields': ('name', 'event_type', 'image', 'image_caption', 'comments')}), 
                ('Event Definition', {'fields' : (('region','map_location'), ('start_date', 'duration', 'season'))}),
                ('Impact', {'fields' : (('deaths', 'people_affected'), 'economical_loss')}) )
                
    inlines = [
        AttributionInline,
    ]
    def _get_map_widget(self, db_field, widget):
        widget = super()._get_map_widget(db_field, widget)
        widget.map_height = "200px"
        widget.map_width = "100%"
        #widget.settings_overrides = {'MIN_ZOOM': 1, 'DEFAULT_ZOOM': 2}
        return widget

