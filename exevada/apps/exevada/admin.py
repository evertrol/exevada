from django.contrib import admin
from django.contrib.gis.db import models as geo_models
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin, LeafletWidget
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from . import models
import io
import csv
import itertools

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


def read_model_analysis_csv(csvfile):

    # List of keys corresponding to the column headings
    keys = ['dataset', 'distribution', 'model', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'eventmag', 'return', 'return_min', 'return_max', 'GMSTnow', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max']

    # Index of (first) line in csv that contains the values
    first_row_index = 20

    csv_rows = list(csv.reader(io.StringIO(csvfile.read().decode('utf-8'))))

    rows = []
    for values in csv_rows[first_row_index:]:
        print(values, len(values))

        # Zip up the values in the row with the keys for each column heading
        params = {k:v for k,v in zip(keys,values)}

        # If the dataset entry is empty (or just whitespace) then assume we have reached the end of the input rows
        if not params['dataset'] or params['dataset'].isspace():
            print('Found row starting with empty Dataset field. Stopping CSV parsing.')
            break

        # If something is provided for dataset, but not distribution then similarly assume this is not an entry row
        if not params['distribution'] or params['distribution'].isspace():
            print('Row has dataset specified, but not distribution. Stopping CSV parsing.')
            break

        # If we think it's a real analysis row, add it to the list.
        rows.append(params)

    return rows


def convert_csv_to_model_analyses(csvfile, attribution):

    # Read in the model analysis parameters from the given csv file
    uploaded_csv_params = read_model_analysis_csv(csvfile)

    # Create a new ModelAnalysis object for each distinct analysis found in the csv
    new_analyses = []
    for params in uploaded_csv_params:

        # Prepare a new entry to the database for this CSV row
        # and link it to the parent Attribution entry
        new_analysis = models.ModelAnalysis()
        new_analysis.attribution = attribution

        print('params=',params, type(params))

        # Convert upper bound infs to blank fields
        for k in ['sigma_max', 'xi_max', 'Delta_I_max', 'PR_max']:
            if params[k] == 'inf':
                params[k] = None

        # Assign values to the corresponding fields in the form
        new_analysis.sigma = params['sigma']
        new_analysis.sigma_min = params['sigma_min']
        new_analysis.sigma_max = params['sigma_max']
        new_analysis.xi = params['xi']
        new_analysis.xi_min = params['xi_min']
        new_analysis.xi_max = params['xi_max']
        new_analysis.Delta_I = params['Delta_I']
        new_analysis.Delta_I_min = params['Delta_I_min']
        new_analysis.Delta_I_max = params['Delta_I_max']
        new_analysis.PR = params['PR']
        new_analysis.PR_min = params['PR_min']
        new_analysis.PR_max = params['PR_max']

        # Set dataset entry
        matching_datasets = list(models.ModelDataSet.objects.filter(model_name=params['dataset']))

        if len(matching_datasets) == 0:
            print(f"No exiting model data sets found matching name '{params['dataset']}'")
            return instance
        elif len(matching_datasets) > 1:
            print(f"Warning: more than one ModelDataSet with name {params['dataset']}. Assigning first matching result.")
        model_dataset = matching_datasets[0]

        print(model_dataset, type(model_dataset))

        new_analysis.dataset = model_dataset

        print(new_analysis, type(new_analysis))

        new_analyses.append(new_analysis)

    return new_analyses


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


class ModelAnalysisAdminForm(forms.ModelForm):
    csvupload = forms.FileField(required=False)

    class Meta:
        fields = [ 'csvupload', 'dataset', 'y_pres', 'y_past', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max', 'comments' ]

    def clean(self):
        print('Called clean()')
        cleaned_data = super(ModelAnalysisAdminForm, self).clean()
        print('Called super clean')
        csvfile = cleaned_data['csvupload']
        if csvfile:
            print('Clean found csvfile:', csvfile, type(csvfile))
            print(cleaned_data, type(cleaned_data))
            cleaned_data['csvupload'] = convert_csv_to_model_analyses(csvfile, cleaned_data['attribution'])

        return cleaned_data

    def save(self, commit=True):
        print("Saving ModelAnalysisAdminForm")

        instance = super(ModelAnalysisAdminForm, self).save(commit=False)

        new_analyses_from_csv = self.cleaned_data['csvupload']

        if new_analyses_from_csv:
            # If we're reading from the uploaded CSV, then we don't want Django
            # to try to commit the present form as well. So set commit to False.
            commit = False

            # Save new model analyses to database
            for new_analysis in new_analyses_from_csv:
                if isinstance(new_analysis, models.ModelAnalysis):
                    new_analysis.save()

        if commit:
            instance.save()
        return instance


class ModelAnalysisInline(admin.TabularInline):
    model = models.ModelAnalysis
    form = ModelAnalysisAdminForm
    formfield_overrides = small_inputs()
    extra = 0
    inlines = []

class AttributionInline(NestedStackedInline):
    model = models.Attribution
    extra = 0
    fieldsets = ( (None, {'fields': (('description', 'location'),)}),
                  ('Method', {'fields': (('variable', 'distribution', 'statistical_method'),)}),
                  ('Synthesis', {'fields' : ('return_period', ('PR', 'PR_min', 'PR_max'), ('Delta_I', 'Delta_I_min', 'Delta_I_max'), 'conclusions')}),
                  ('Dissemination', {'fields' : ('contact', 'webpage', 'papers', 'press_communication', ('research_data', 'research_data_doi'))}), )
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

