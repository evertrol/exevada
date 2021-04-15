from django import forms
from .widgets import AreaInput
from . import models
import io
import csv


def read_model_analysis_csv(csvfile):

    # List of keys corresponding to the column headings
    keys = ['dataset', 'n_members', 'statmodel', 'seasonalcycle', 'spatialpattern', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'statprop', 'conclusion', 'include_model', 'threshold300y', 'GMSTnow',  'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max', 'GMSTfuture', 'PR_future', 'PR_min_future', 'PR_max_future', 'Delta_I_future', 'Delta_I_min_future', 'Delta_I_max_future']

    # Index of (first) line in csv that contains the values
    first_row_index = 9

    # CSV uploaded as bytes - assume UTF-8 encoding
    csv_rows = list(csv.reader(io.StringIO(csvfile.read().decode('utf-8'))))

    rows = []
    for values in csv_rows[first_row_index:]:

        # Zip up the values in the row with the keys for each column heading
        params = {k:v for k,v in zip(keys,values)}

        # If the 'Include model?' field is empty (or just whitespace) then assume we have reached the end of the input rows
        if not params['include_model'] or params['include_model'].isspace():
            print('Log: Found row with empty "Include model?" field. Stopping CSV parsing.')
            break

        rows.append(params)

    return rows


def read_observation_analysis_csv(csvfile):

    # List of keys corresponding to the column headings
    keys = ['dataset', 'distribution', 'statmodel', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'eventmag', 'T_return', 'T_return_min', 'T_return_max', 'GMSTnow', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max']

    # Index of (first) line in csv that contains the values
    first_row_index = 20

    # CSV uploaded as bytes - assume UTF-8 encoding
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


def convert_csv_to_model_analyses(csvfile, create_dataset_if_not_found=False):

    # Read in the model analysis parameters from the given csv file
    uploaded_csv_params = read_model_analysis_csv(csvfile)

    # Check that at least one row of values was found
    if len(uploaded_csv_params) == 0:
        raise forms.ValidationError('No valid model analysis rows found in uploaded CSV')

    # Create a new ModelAnalysis object for each distinct analysis found in the csv
    new_analyses = []
    datasets_lookup = {}
    for params in uploaded_csv_params:

        # If 'Include Model' is not 'Y' or 'N' then throw error
        include_model_str = params['include_model']
        if include_model_str != 'Y' and include_model_str != 'N':
            raise ValidationError(f'"Include Model?" field must be either "Y" or "N". Found "{include_model_str}".')

        if include_model_str == 'N':
            continue

        # Prepare a new entry to the database for this CSV row
        new_analysis = models.ModelAnalysis()

        # Convert upper bound infs to blank fields and throw error if -inf provided
        for k in ['sigma_max', 'xi_max', 'Delta_I_max', 'PR_max']:
            if params[k] == 'inf':
                params[k] = None
            elif params[k] == '-inf':
                raise forms.ValidationError(f'{k} is -inf, but this is not physical.')

        # Convert lower bound -infs to blank fields and throw error if inf provided
        for k in ['sigma_min', 'xi_min', 'Delta_I_min', 'PR_min']:
            if params[k] == '-inf':
                params[k] = None
            elif params[k] == 'inf':
                raise forms.ValidationError(f'{k} is inf, but this is not physical.')

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

        new_analysis.dataset = model_dataset
        new_analyses.append(new_analysis)

    return new_analyses


def convert_csv_to_observation_analyses(csvfile):

    # Read in the observation analysis parameters from the given csv file
    uploaded_csv_params = read_observation_analysis_csv(csvfile)

    # Check that at least one row of values was found
    if len(uploaded_csv_params) == 0:
        raise forms.ValidationError('No valid observation analysis rows found in uploaded CSV')

    # Create a new ObservationAnalysis object for each distinct analysis found in the csv
    new_analyses = []
    datasets_lookup = {}
    for i, params in enumerate(uploaded_csv_params):

        # Prepare a new entry to the database for this CSV row
        new_analysis = models.ObservationAnalysis()

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

        # Enure that return periods are integer values (if not blank)
        for k in ['T_return', 'T_return_min', 'T_return_max']:
            if params[k] is not None:
                try:
                    params[k] = int(params[k])
                except ValueError:
                    print(f'Warning: {k} contains value {params[k]} which does not convert to an integer. Attempting forced conversion with rounding.')
                    try:
                        params[k] = int(round(float(params[k])))
                    except ValueError:
                        raise forms.ValidationError(f'In analysis row {i}, field {k}: Could not convert {params[k]} to integer.')

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

        new_analysis.dataset = observation_dataset
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
        cleaned_data = super(ObservationAnalysisAdminForm, self).clean()
        csvfile = cleaned_data['csvupload']
        if csvfile:
            # Convert the uploaded csv file to a list of new ObservationAnalysis instances.
            # Store these in cleaned_data so that the save() method can find and commit them to the db.
            cleaned_data['csvupload'] = convert_csv_to_observation_analyses(csvfile)

            # Validate each new model instance so that any exceptions are raised here and communicated to the user
            # (rather than occurring in the save() call which causes everything to error out)
            for i, new_observation_instance in enumerate(cleaned_data['csvupload']):
                try:
                    new_observation_instance.clean_fields(exclude='attribution')
                except forms.ValidationError as e:
                    augmented_error_msg = f'[In uploaded CSV] Observation analysis {i+1}: {e.__str__()}'
                    raise forms.ValidationError(augmented_error_msg)
        else:
            # Ensure that the dataset field is set in cases where form is being filled in manually (no CSV uploaded)
            if not cleaned_data['dataset']:
                raise forms.ValidationError('Dataset field cannot be left blank.')

        return cleaned_data

    def save(self, commit=True):

        instance = super(ObservationAnalysisAdminForm, self).save(commit=False)
        new_analyses_from_csv = self.cleaned_data['csvupload']

        if new_analyses_from_csv:
            # If we're reading from the uploaded CSV, then we don't want Django
            # to try to commit the present form as well. So set commit to False.
            commit = False

            # Save new observation analyses to database (and their corresponding ModelDataSets if new
            for new_analysis in new_analyses_from_csv:
                if isinstance(new_analysis, models.ObservationAnalysis):
                    # Save the (potentially new) dataset object first
                    new_analysis.dataset.save()

                    # Set the attribution to the parent Attribution model's key
                    # and save this analysis to the DB
                    new_analysis.attribution = instance.attribution
                    new_analysis.save()

        if commit:
            instance.save()
        return instance


class ModelAnalysisAdminForm(forms.ModelForm):
    csvupload = forms.FileField(required=False)

    class Meta:
        fields = [ 'csvupload', 'dataset', 'y_pres', 'y_past', 'sigma', 'sigma_min', 'sigma_max', 'xi', 'xi_min', 'xi_max', 'PR', 'PR_min', 'PR_max', 'Delta_I', 'Delta_I_min', 'Delta_I_max', 'comments' ]

    def __init__(self, *args, **kwargs):
        super(ModelAnalysisAdminForm, self).__init__(*args, **kwargs)
        self.fields['csvupload'].widget.attrs.update({'accept': '.csv'})

    def clean(self):
        cleaned_data = super(ModelAnalysisAdminForm, self).clean()
        csvfile = cleaned_data['csvupload']
        if csvfile:
            # Convert the uploaded csv file to a list of new ModelAnalysis instances.
            # Store these in cleaned_data so that the save() method can find and commit them to the db.
            cleaned_data['csvupload'] = convert_csv_to_model_analyses(csvfile, create_dataset_if_not_found=False)

            # Validate each new model instance so that any exceptions are raised here and communicated to the user
            # (rather than occurring in the save() call which causes everything to error out)
            for i, new_analysis_instance in enumerate(cleaned_data['csvupload']):
                try:
                    new_analysis_instance.clean_fields(exclude='attribution')
                except forms.ValidationError as e:
                    augmented_error_msg = f'[In uploaded CSV] Model analysis {i+1}: {e.__str__()}'
                    raise forms.ValidationError(augmented_error_msg)
        else:
            # Ensure that the dataset field is set in cases where form is being filled in manually (no CSV uploaded)
            if not cleaned_data['dataset']:
                raise forms.ValidationError('Dataset field cannot be left blank.')

        return cleaned_data

    def save(self, commit=True):

        instance = super(ModelAnalysisAdminForm, self).save(commit=False)
        new_analyses_from_csv = self.cleaned_data['csvupload']

        if new_analyses_from_csv:
            # If we're reading from the uploaded CSV, then we don't want Django
            # to try to commit the present form as well. So set commit to False.
            commit = False

            # Save new model analyses to database (and their corresponding ModelDataSets if new
            for new_analysis in new_analyses_from_csv:
                if isinstance(new_analysis, models.ModelAnalysis):
                    # Save the (potentially new) dataset object first
                    new_analysis.dataset.save()

                    # Set the attribution to the parent Attribution model's key
                    # and save this analysis to the DB
                    new_analysis.attribution = instance.attribution
                    new_analysis.save()

        if commit:
            instance.save()
        return instance
