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

        # Zip up the values in the row with the keys for each column heading
        params = {k:v for k,v in zip(keys,values)}

        # If the dataset entry is empty (or just whitespace) then assume we have reached the end of the input rows
        if not params['dataset'] or params['dataset'].isspace():
            print('Log: Found row starting with empty Dataset field. Stopping CSV parsing.')
            break

        # If something is provided for dataset, but not distribution then similarly assume this is not an entry row
        if not params['distribution'] or params['distribution'].isspace():
            print('Log: Row has dataset specified, but not distribution. Stopping CSV parsing.')
            break

        # If we think it's a real analysis row, add it to the list.
        rows.append(params)

    return rows


def convert_csv_to_model_analyses(csvfile, attribution, create_dataset_if_not_found=False):

    # Read in the model analysis parameters from the given csv file
    uploaded_csv_params = read_model_analysis_csv(csvfile)

    # Check that at least one row of values was found
    if len(uploaded_csv_params) == 0:
        raise forms.ValidationError('No valid model analysis rows found in uploaded CSV')

    # Create a new ModelAnalysis object for each distinct analysis found in the csv
    new_analyses = []
    datasets_lookup = {}
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

        # Look for existing dataset with this name in lookup
        dataset_name = params['dataset']
        if dataset_name in datasets_lookup:
            model_dataset = datasets_lookup[dataset_name]
        else:
            try:
                model_dataset = models.ModelDataSet.objects.get(model_name=dataset_name)
            except models.ModelDataSet.DoesNotExist:
                if create_dataset_if_not_found:
                    print(f"Log: No existing model data sets found matching name '{dataset_name}'. Creating new dataset.")
                    model_dataset = models.ModelDataSet()
                    model_dataset.model_name = dataset_name
                else:
                    raise forms.ValidationError(f'A Model Data set with name "{dataset_name}" was not found in the database. Please create it first.')

            datasets_lookup[params['dataset']] = model_dataset

        print(model_dataset, type(model_dataset))

        new_analysis.dataset = model_dataset

        print(new_analysis, type(new_analysis))

        new_analyses.append(new_analysis)

    return new_analyses


def read_observation_analysis_csv(csvfile):

    # List of keys corresponding to the column headings
    keys = ['dataset', 'distribution', 'model', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'eventmag', 'T_return', 'T_return_min', 'T_return_max', 'GMSTnow', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max']

    # Index of (first) line in csv that contains the values
    first_row_index = 20

    csv_rows = list(csv.reader(io.StringIO(csvfile.read().decode('utf-8'))))

    rows = []
    for values in csv_rows[first_row_index:]:

        # Zip up the values in the row with the keys for each column heading
        params = {k:v for k,v in zip(keys,values)}

        # If the dataset entry is empty (or just whitespace) then assume we have reached the end of the input rows
        if not params['dataset'] or params['dataset'].isspace():
            print('Log: Found row starting with empty Dataset field. Stopping CSV parsing.')
            break

        # If something is provided for dataset, but not distribution then similarly assume this is not an entry row
        if not params['distribution'] or params['distribution'].isspace():
            print('Log: Row has dataset specified, but not distribution. Stopping CSV parsing.')
            break

        # If we think it's a real analysis row, add it to the list.
        rows.append(params)

    return rows


def convert_csv_to_observation_analyses(csvfile, attribution):

    print('attribution=', attribution, type(attribution))

    # Read in the observation analysis parameters from the given csv file
    uploaded_csv_params = read_observation_analysis_csv(csvfile)

    # Check that at least one row of values was found
    if len(uploaded_csv_params) == 0:
        raise forms.ValidationError('No valid observation analysis rows found in uploaded CSV')

    # Create a new ObservationAnalysis object for each distinct analysis found in the csv
    new_analyses = []
    datasets_lookup = {}
    for params in uploaded_csv_params:

        # Prepare a new entry to the database for this CSV row
        # and link it to the parent Attribution entry
        new_analysis = models.ObservationAnalysis()
        new_analysis.attribution = attribution

        print('params=',params, type(params))

        # Convert upper bound infs to blank fields and throw error if -inf provided
        for k in ['sigma_max', 'xi_max', 'Delta_I_max', 'PR_max', 'T_return_max']:
            if params[k] == 'inf':
                params[k] = None
            elif params[k] == '-inf':
                raise forms.ValidationError(f'{k} is -inf, but this is not physical.')

        # Convert lower bound -infs to blank fields and throw error if inf provided
        for k in ['sigma_min', 'xi_min', 'Delta_I_min', 'PR_min', 'T_return_min']:
            if params[k] == '-inf':
                params[k] = None
            elif params[k] == 'inf':
                raise forms.ValidationError(f'{k} is inf, but this is not physical.')

        # Assign values to the corresponding fields in the form
        new_analysis.variable_value = params['eventmag']
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
        new_analysis.T_return = params['T_return']
        new_analysis.T_return_min = params['T_return_min']
        new_analysis.T_return_max = params['T_return_max']

        # Look for existing dataset with this name in lookup
        if params['dataset'] in datasets_lookup:
            observation_dataset = datasets_lookup[params['dataset']]
        else:
            try:
                observation_dataset = models.ObservationDataSet.objects.get(name=params['dataset'])
            except models.ObservationDataSet.DoesNotExist:
                print(f"Log: No existing observation data sets found matching name '{params['dataset']}'. Creating new dataset.")
                observation_dataset = models.ObservationDataSet()
                observation_dataset.name = params['dataset']

            datasets_lookup[params['dataset']] = observation_dataset

        print(observation_dataset, type(observation_dataset))

        new_analysis.dataset = observation_dataset

        print('NEW ANALYSIS', new_analysis, type(new_analysis))

        new_analyses.append(new_analysis)

    return new_analyses


class ObservationAnalysisAdminForm(forms.ModelForm):
    csvupload = forms.FileField(required=False)

    class Meta:
        fields = [ 'csvupload', 'dataset', 'variable_value', 'y_pres', 'y_past', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max', 'T_return', 'T_return_min', 'T_return_max', 'comments' ]

    def __init__(self, *args, **kwargs):
        super(ObservationAnalysisAdminForm, self).__init__(*args, **kwargs)
        self.fields['csvupload'].widget.attrs.update({'accept': '.csv'})

    def clean(self):
        print('Log: Called clean()')
        cleaned_data = super(ObservationAnalysisAdminForm, self).clean()
        csvfile = cleaned_data['csvupload']
        if csvfile:
            print(cleaned_data)
            print(cleaned_data['attribution'])


            # Convert the uploaded csv file to a list of new ObservationAnalysis instances.
            # Store these in cleaned_data so that the save() method can find and commit them to the db.
            cleaned_data['csvupload'] = convert_csv_to_observation_analyses(csvfile, cleaned_data['attribution'])

            # Validate each new model instance so that any exceptions are raised here and communicated to the user
            # (rather than occurring in the save() call which causes everything to error out)
            for i, new_observation_instance in enumerate(cleaned_data['csvupload']):
                print('CLEAN', i, new_observation_instance, type(new_observation_instance), new_observation_instance.attribution)

                try:
                    new_observation_instance.full_clean()
                except forms.ValidationError as e:
                    print(e, type(e))
                    augmented_error_msg = f'[In uploaded CSV] Observation analysis {i+1}: {e.__str__()}'
                    raise forms.ValidationError(augmented_error_msg)

        return cleaned_data

    def save(self, commit=True):
        print("Log: Saving ObservationAnalysisAdminForm")

        instance = super(ObservationAnalysisAdminForm, self).save(commit=False)

        new_analyses_from_csv = self.cleaned_data['csvupload']

        if new_analyses_from_csv:
            # If we're reading from the uploaded CSV, then we don't want Django
            # to try to commit the present form as well. So set commit to False.
            commit = False

            # Save new observation analyses to database (and their corresponding ModelDataSets if new
            for new_analysis in new_analyses_from_csv:
                if isinstance(new_analysis, models.ObservationAnalysis):
                    new_analysis.dataset.save()
                    new_analysis.save()

        if commit:
            instance.save()
        return instance


class ObservationAnalysisInline(admin.TabularInline):
    model = models.ObservationAnalysis
    form = ObservationAnalysisAdminForm
    extra = 0
    inlines = []
    formfield_overrides = small_inputs()


class ModelAnalysisAdminForm(forms.ModelForm):
    csvupload = forms.FileField(required=False)

    class Meta:
        fields = [ 'csvupload', 'dataset', 'y_pres', 'y_past', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max', 'comments' ]

    def __init__(self, *args, **kwargs):
        super(ModelAnalysisAdminForm, self).__init__(*args, **kwargs)
        self.fields['csvupload'].widget.attrs.update({'accept': '.csv'})

    def clean(self):
        print('Log: Called clean()')
        cleaned_data = super(ModelAnalysisAdminForm, self).clean()
        csvfile = cleaned_data['csvupload']
        if csvfile:
            # Convert the uploaded csv file to a list of new ModelAnalysis instances.
            # Store these in cleaned_data so that the save() method can find and commit them to the db.
            cleaned_data['csvupload'] = convert_csv_to_model_analyses(csvfile, cleaned_data['attribution'])

            # Validate each new model instance so that any exceptions are raised here and communicated to the user
            # (rather than occurring in the save() call which causes everything to error out)
            for i, new_analysis_instance in enumerate(cleaned_data['csvupload']):
                try:
                    new_analysis_instance.full_clean()
                except forms.ValidationError as e:
                    print(e, type(e))
                    augmented_error_msg = f'[In uploaded CSV] Model analysis {i+1}: {e.__str__()}'
                    raise forms.ValidationError(augmented_error_msg)

        return cleaned_data

    def save(self, commit=True):
        print("Log: Saving ModelAnalysisAdminForm")

        instance = super(ModelAnalysisAdminForm, self).save(commit=False)

        new_analyses_from_csv = self.cleaned_data['csvupload']

        if new_analyses_from_csv:
            # If we're reading from the uploaded CSV, then we don't want Django
            # to try to commit the present form as well. So set commit to False.
            commit = False

            # Save new model analyses to database (and their corresponding ModelDataSets if new
            for new_analysis in new_analyses_from_csv:
                if isinstance(new_analysis, models.ModelAnalysis):
                    new_analysis.dataset.save()
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

