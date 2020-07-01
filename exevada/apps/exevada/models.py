from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    name = models.CharField(max_length=256, help_text="Location name")
    area = models.GeometryField(help_text="Geographic location or region")
    description =  models.TextField(blank=True)
    def __str__(self):
        return self.name


class EventType(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text="Event type")
    description =  models.TextField(blank=True)
    def __str__(self):
        return self.name


class DistributionType(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text="Distribution name")
    abbreviation =  models.CharField(max_length=32, help_text="Abbreviation", blank=True)
    has_shape_parameter = models.BooleanField(help_text="Does the distribution contain tuneable shape parameter")
    def __str__(self):
        return self.name


class StatisticalMethod(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text="Name of the method")
    description =  models.TextField(help_text="Short description of the method", blank=True)
    covariate = models.CharField(max_length=32, help_text="Proxy for anthropogenic forcing")
    dispersion_fit = models.BooleanField(help_text="Does the method fit the dispersion (sigma/mu) or scale (sigma) parameter?")
    def __str__(self):
        return self.name


class AttributionVariable(models.Model):
    short_name = models.CharField(max_length=16, help_text="Abbreviated variable name")
    long_name = models.CharField(max_length=128, help_text="Full variable name", blank=True)
    description = models.TextField(help_text="Description", blank=True)
    unit = models.CharField(max_length=64, help_text="Unit of the variable", blank=True)
    unit_symbol = models.CharField(max_length=16, help_text="Unit symbol of the variable", blank=True)
    delta_I_unit_symbol = models.CharField(max_length=16, help_text="Unit symbol of intensity change", blank=True)
    def __str__(self):
        return self.short_name


class ObservationDataSet(models.Model):
    name = models.CharField(max_length=256, help_text="Observation dataset")
    url = models.URLField(max_length=512, blank=True)
    description = models.TextField(help_text="Dataset description", blank=True)
    doi = models.CharField(max_length=256, help_text="DOI of dataset", blank=True)
    papers = models.ManyToManyField("JournalPaper", help_text="Reviewed papers describing the attribution", blank=True)
    def __str__(self):
        return self.name


class ModelDataSet(models.Model):
    model_name = models.CharField(max_length=128, help_text="Model output dataset")
    model_description = models.TextField(help_text="Model description", blank=True)
    experiment = models.CharField(max_length=512, help_text="Experiment")
    experiment_description = models.TextField(help_text="Experiment description", blank=True)
    url = models.URLField(max_length=512, blank=True)
    doi = models.CharField(max_length=256, help_text="DOI of dataset", blank=True)
    papers = models.ManyToManyField("JournalPaper", help_text="Reviewed papers describing the attribution", blank=True)
    def __str__(self):
        return ' '.join([self.model_name, self.experiment])


class SynthesisBase(models.Model):
    PR = models.FloatField(help_text="Probability ratio", validators=[MinValueValidator(0.0)], default=0.0)
    PR_min = models.FloatField(help_text="Probability ratio lower bound", null=True, blank=True)
    PR_max = models.FloatField(help_text="Probability ratio upper bound", null=True, blank=True)
    Delta_I = models.FloatField(help_text="Intensity change", default=0.0, 
                                validators=[MinValueValidator(0), MaxValueValidator(100)])
    Delta_I_min = models.FloatField(help_text="Intensity change lower bound", null=True, blank=True, 
                                validators=[MinValueValidator(0), MaxValueValidator(100)])
    Delta_I_max = models.FloatField(help_text="Intensity change upper bound", null=True, blank=True, 
                                validators=[MinValueValidator(0), MaxValueValidator(100)])
    comments = models.TextField(help_text="Remarks", blank=True)
    class Meta:
        abstract = True


class AnalysisBase(SynthesisBase):
    sigma = models.FloatField(help_text="Fitted scale/dispersion parameter", default=0.0)
    sigma_min = models.FloatField(help_text="Scale/dispersion parameter lower bound", null=True, blank=True)
    sigma_max = models.FloatField(help_text="Scale/dispersion parameter upper bound", null=True, blank=True)
    xi = models.FloatField(help_text=   "Fitted shape parameter", null=True, blank=True)
    xi_min = models.FloatField(help_text="Shape parameter lower bound", null=True, blank=True)
    xi_max = models.FloatField(help_text="Shape parameter upper bound", null=True, blank=True)
    y_past = models.PositiveIntegerField(help_text="Starting year of the analysis", null=True, blank=True)
    y_pres = models.PositiveIntegerField(help_text="Ending year of the analysis")
    trend = models.FloatField(help_text="Calculated trend", null=True, blank=True)
    class Meta:
        abstract = True


class Publication(models.Model):
    title = models.CharField(max_length=1024, help_text="Publication title")
    doi = models.CharField(max_length=256, help_text="DOI (no URL) of related publication", blank=True)
    authors = models.CharField(max_length=1024, help_text="Author list")
    date = models.DateField(help_text="Publication date")
    url = models.URLField(max_length=512, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        abstract=True


class JournalPaper(Publication):
    journal = models.CharField(max_length=256, help_text="Journal")
    issue = models.IntegerField(help_text="Issue", null=True, blank=True)


class PressCommunication(Publication):
    medium = models.CharField(max_length=256, help_text="Medium")


class ObservationAnalysis(AnalysisBase):
    attribution = models.ForeignKey("Attribution", on_delete=models.CASCADE, related_name="observations")
    variable_value = models.FloatField(help_text="Variable value for this observation dataset", default=0.0)
    dataset = models.ForeignKey("ObservationDataSet", on_delete=models.CASCADE)
    T_return = models.PositiveIntegerField(help_text="Return period (yr)", validators=[MinValueValidator(0.0)])
    T_return_min = models.PositiveIntegerField(help_text="Return period lower bound (yr)", validators=[MinValueValidator(0.0)], null=True, blank=True)
    T_return_max = models.PositiveIntegerField(help_text="Return period upper bound (yr)", validators=[MinValueValidator(0.0)], null=True, blank=True)
    def __str__(self):
        return '-'.join([str(self.attribution), str(self.dataset)])
    class Meta:
        verbose_name_plural = "observation analyses"


class ModelAnalysis(AnalysisBase):
    class EvaluationOutcome(models.TextChoices):
        Good = "good", _("Good")
        Bad = "bad", _("Bad")
        Reasonable = "reasonable", _("Reasonable")
    attribution = models.ForeignKey("Attribution", on_delete=models.CASCADE, related_name="models")
    dataset = models.ForeignKey("ModelDataSet", on_delete=models.CASCADE)
    variable_threshold = models.FloatField(help_text="Variable threshold corresponding to attributed return period", default=0.0)
    seasonal_cycle = models.CharField(max_length=32, choices=EvaluationOutcome.choices)
    spatial_pattern = models.CharField(max_length=32, choices=EvaluationOutcome.choices)
    def __str__(self):
        return '-'.join([str(self.attribution), str(self.dataset)])
    class Meta:
        verbose_name_plural = "model analyses"


class Attribution(SynthesisBase):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="attributions")
    attribution_request = models.TextField(help_text="Request for attribution", blank=True)
    description = models.CharField(max_length=256, help_text="Short descriptive string", unique=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    variable = models.ForeignKey("AttributionVariable", on_delete=models.CASCADE)
    distribution = models.ForeignKey("DistributionType", on_delete=models.CASCADE)
    statistical_method = models.ForeignKey("StatisticalMethod", on_delete=models.CASCADE)
    return_period = models.PositiveIntegerField(help_text="Rounded return period (yr)", validators=[MinValueValidator(0.0)], null=True)
    conclusions = models.TextField(help_text="Synthesis conclusions", blank=True)
    contact = models.CharField(max_length=1024, help_text="Contact email adress", blank=True)
    webpage = models.URLField(max_length=512, help_text="Relevant web page", blank=True, default="https://attribution.climate.copernicus.eu")
    papers = models.ManyToManyField("JournalPaper", help_text="Reviewed papers describing the attribution", blank=True)
    press_communication = models.ManyToManyField("PressCommunication", help_text="Press communication related to the attribution", blank=True)
    def __str__(self):
        return ' '.join([str(self.event), self.description])


class Event(models.Model):
    class Season(models.TextChoices):
        DJJ = "DJJ", _("Dec-Feb")
        MAM = "MAM", _("Mar-May")
        JJA = "JJA", _("Jun-Aug")
        SON = "SON", _("Sep-Nov")
    name = models.CharField(max_length=128, help_text="Short, descriptive name or title for this event")
    region = models.CharField(max_length=256, help_text="Geographic region where the event was observed")
    event_type = models.ForeignKey("EventType", on_delete=models.CASCADE, help_text="Type of event")
    start_date = models.DateField(help_text="Event starting date")
    duration = models.PositiveIntegerField(help_text="Duration of the event (nr of days)")
    season = models.CharField(max_length=8, choices=Season.choices, help_text="Season", default=Season.DJJ)
    deaths = models.PositiveIntegerField(help_text="Number of deaths", blank=True, null=True)
    people_affected = models.PositiveIntegerField(help_text="Number of people affected", blank=True, null=True)
    economical_loss = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated economic loss in Meuro", blank=True, null=True)
    comments = models.TextField(help_text="Remarks", blank=True)
    image = models.ImageField(upload_to='event_artwork')
    def __str__(self):
        return self.name