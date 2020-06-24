from django.contrib import admin
from django.contrib.gis import admin as gisadmin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from . import models

@admin.register(models.EventType)
class EventType(admin.ModelAdmin):
    pass

@admin.register(models.Location)
class Location(gisadmin.GeoModelAdmin):
    default_lat = 50
    default_lon = 16
    default_zoom = 4
    display_wkt = True
    layerswitcher = False
    def get_map_widget(self, db_field):
        olmap = super().get_map_widget(db_field)
        olmap.params['is_generic'] = False
        olmap.params['is_linestring'] = False
        olmap.params['is_point'] = True
        olmap.params['is_polygon'] = True
        return olmap

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
    fields = (  ('dataset', 'variable_threshold', 'trend' ),
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
                  ('Dissemination', {'fields' : ('contact', 'webpage', 'papers', 'press_releases')}))
    inlines = [ObservationAnalysisInline, ModelAnalysisInline]

@admin.register(models.Event)
class Event(NestedModelAdmin):
    fieldsets = ( (None, {'fields': ('name', 'event_type', 'image')}), 
                ('Event Definition', {'fields' : ('region', ('start_date', 'duration', 'season'))}),
                ('Impact', {'fields' : (('deaths', 'people_affected'), 'economical_loss', 'ecological_impact')}),
                (None, {'fields': ['comments']} ))
    inlines = [
        AttributionInline,
    ]
