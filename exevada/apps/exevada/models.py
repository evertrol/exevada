from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    name = models.CharField(max_length=256, unique=True,
                            help_text="Region name")
    area = models.MultiPolygonField(help_text="One or more polygons making up the region")
    def __str__(self):
        return self.name


class AnalysisMixin(models.Model):
    attribution = models.ForeignKey("Attribution", on_delete=models.CASCADE, related_name="%(class)ss")
    mu = models.FloatField(help_text="Fitted location parameter")
    sigma = models.FloatField(help_text="Fitted scale parameter", validators=[MinValueValidator(0.0)])
    xi = models.FloatField(help_text="Fitted shape parameter")
    return_period = models.FloatField(help_text="Return period (yr)", validators=[MinValueValidator(0.0)], default=0.0)
    return_period_lower_bound = models.FloatField(help_text="Return period lower bound", validators=[MinValueValidator(0.0)], default=0.0)
    return_period_upper_bound = models.FloatField(help_text="Return period upper bound", validators=[MinValueValidator(0.0)], default=0.0)
    pr = models.FloatField(help_text="Probability ratio", validators=[MinValueValidator(0.0)], default=0.0)
    delta_I = models.FloatField(help_text="Change in intensity", default=0.0)
    comments = models.TextField(help_text="Remarks", default="none")
    class Meta:
        abstract = True


class ObservationDataSet(models.Model):
    name = models.CharField(max_length=256, help_text="Observation dataset")
    url = models.URLField(max_length=512, blank=True)
    description = models.TextField(help_text="Dataset description")
    doi = models.CharField(max_length=256, help_text="DOI of dataset", unique=True, default="none")
    def __str__(self):
        return self.name


class ModelDataSet(models.Model):
    model_name = models.CharField(max_length=128, help_text="Model output dataset")
    model_description = models.TextField(help_text="Model description")
    experiment = models.CharField(max_length=512, help_text="Experiment")
    experiment_description = models.TextField(help_text="Experiment description")
    url = models.URLField(max_length=512, blank=True)
    doi = models.CharField(max_length=256, help_text="DOI of dataset", unique=True, default="none")
    def __str__(self):
        return ' '.join([self.model_name, self.experiment])


class Event(models.Model):
    class Season(models.TextChoices):
        DJJ = "DJJ", _("Dec-Feb")
        MAM = "MAM", _("Mar-May")
        JJA = "JJA", _("Jun-Aug")
        SON = "SON", _("Sep-Nov")
    name = models.CharField(max_length=128,
                            help_text="Short, descriptive name or title for this event")
    region = models.ForeignKey("Region", on_delete=models.CASCADE)
    startdate = models.DateField(help_text="Event starting date")
    duration = models.PositiveIntegerField(help_text="Duration of the event (nr of days)")
    season = models.CharField(max_length=8, choices=Season.choices, help_text="Season", default=Season.DJJ)
    deaths = models.PositiveIntegerField(help_text="Number of deaths", default=0)
    people_affected = models.PositiveIntegerField(help_text="Number of people affected", default=0)
    economical_loss = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated economic loss in Keuro", default=0)
    ecological_impact = models.CharField(max_length=2048, help_text="Ecological impact", default="none")
    attribution_request = models.CharField(max_length=1024, help_text="Request for attribution", default="none")
    comments = models.TextField(help_text="Remarks", default="none")
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('event', args=[self.pk])


#TODO: Add region and time scale for variable
class Attribution(models.Model):
    class MeteoVariable(models.TextChoices):
        Tmax  = "Tmax", _("maximum temperature")
        Tmin  = "Tmin", _("minimum temperature")
        Tmean = "Tmean", _("mean temperature")
        Pr    = "Pr", _("precipitation")
    class DistributionType(models.TextChoices):
        Gauss = "Gauss", _("Gauss")
        GPD   = "Generalized Pareto", _("generalized Pareto")
        GEV = "Generalized Extreme Value", _("generalized extreme value")
        Gumbel = "Gumbel", _("Gumbel")
        Gamma = "Gamma", _("gamma")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="attributions")
    description = models.CharField(max_length=256, help_text="Short descriptive string")
    variable = models.CharField(max_length=16, choices=MeteoVariable.choices, help_text="Event variable", default=MeteoVariable.Tmax)
    fitted_distribution = models.CharField(max_length=64, choices=DistributionType.choices, help_text="Fitted distribution", default=DistributionType.GEV)
    pr = models.FloatField(help_text="Synthesis probability ratio", validators=[MinValueValidator(0.0)], default=0.0)
    delta_i = models.FloatField(help_text="Synthesis change in intensity", default=0.0)
    conclusions = models.TextField(help_text="Synthesis conclusions", default="none")
    contact = models.CharField(max_length=1024, help_text="Contact email adress", default="none")
    webpage = models.URLField(max_length=512, help_text="Relevant web page", blank=True, default="https://attribution.climate.copernicus.eu")
    def __str__(self):
        return ' '.join([str(self.event), self.description])


class Publication(models.Model):
    subject = models.ForeignKey("Attribution", on_delete=models.CASCADE, related_name="%(class)ss")
    title = models.CharField(max_length=1024, help_text="Publication title", default="none")
    doi = models.CharField(max_length=256, help_text="DOI (no URL) of related publication", unique=True, default="none")
    authors = models.CharField(max_length=1024, help_text="Author list", default="")
    date = models.DateField(help_text="Publication date")
    url = models.URLField(max_length=512, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        abstract=True


class JournalPaper(Publication):
    journal = models.CharField(max_length=256, help_text="Journal")


class PressCommunication(Publication):
    medium = models.CharField(max_length=256, help_text="Medium")


class ObservationAnalysis(AnalysisMixin):
    dataset = models.ForeignKey("ObservationDataSet", on_delete=models.CASCADE)
    value = models.FloatField(help_text="Variable value for this observation dataset", default=0.0)
    def __str__(self):
        return '-'.join([str(super(self).attribution), str(self.dataset)])
    class Meta:
        verbose_name_plural = "observation analyses"


class ModelAnalysis(AnalysisMixin):
    dataset = models.ForeignKey("ModelDataSet", on_delete=models.CASCADE)
    trend = models.FloatField(help_text="Trend", default=0.0)
    def __str__(self):
        return '-'.join([str(super(self).attribution), str(self.dataset)])
    class Meta:
        verbose_name_plural = "model analyses"
