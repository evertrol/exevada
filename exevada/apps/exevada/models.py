from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


PR_VALIDATOR = [MinValueValidator(0), MaxValueValidator(1)]


class Region(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            help_text="Region name")
    area = models.MultiPolygonField(help_text="One or more polygons making up the region")
    #event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='')


class Season(models.Model):
    """Season given by a starting and ending month

    Not the usual djf, mam, jja or son seasons

    """

    MONTHS = [
        (1, "January"),
        (2, "Februari"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    ]

    start = models.IntegerField(choices=MONTHS, help_text="Starting month")
    end = models.IntegerField(choices=MONTHS, help_text="Ending month")
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='season')


class Event(models.Model):
    name = models.CharField(max_length=512,
                            help_text="Short, descriptive name or title for this event")
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    startdate = models.DateField(help_text="Event starting date")
    duration = models.PositiveIntegerField(help_text="Duration of the event "
                                           "in number of (whole) days")
    variable = models.CharField(max_length=255, help_text="Event variable")
    fitted_distribution = models.CharField(max_length=512, help_text="Distribution fitted")
    impact = models.OneToOneField('Impact', on_delete=models.CASCADE)
    synthesis = models.OneToOneField('Synthesis', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
            return reverse('event', args=[self.pk])


class Impact(models.Model):
    deaths = models.DecimalField(max_digits=12, decimal_places=2, help_text="Number of deaths")
    affected = models.DecimalField(max_digits=12, decimal_places=2, help_text="Number of people affected")
    request = models.CharField(max_length=1024, help_text="Request for attribution")
    comments = models.TextField(help_text="Remarks")

    def __str__(self):
        return self.comments[:80]


class Synthesis(models.Model):
    pr = models.FloatField(validators=PR_VALIDATOR,
                           help_text="Probability ratio")
    delta_i = models.FloatField(help_text="Change in intensity")
    conclusions = models.TextField(help_text="Conclusions")
    contact = models.CharField(max_length=1024, help_text="Contact (e.g., lead author)")
    webpage = models.URLField(max_length=512, help_text="Relevant web page")
    doi = models.CharField(max_length=255, help_text="DOI (no URL) of related "
                           "peer-review publication")

    class Meta:
        verbose_name_plural = 'syntheses'

    def __str__(self):
        return self.conclusions[:80]


class FitParameters(models.Model):
    obsdataset = models.ForeignKey('ObsDataset', on_delete=models.CASCADE,
                                   related_name="best_fit_value")
    mu = models.FloatField(help_text="Mu value")
    sigma = models.FloatField(help_text="Sigma value")
    xi = models.FloatField(help_text="Xi value")
    alpha = models.FloatField(help_text="Alpha value")

    class Meta:
        verbose_name_plural = 'fit parameters'


class ReturnTime(models.Model):
    obsdataset = models.ForeignKey('ObsDataset', on_delete=models.CASCADE,
                                   related_name="return_period")
    value = models.FloatField(help_text="Best fit value")
    lower = models.FloatField(help_text="Lower bound")
    upper = models.FloatField(help_text="Upper bound")




class ObsDataset(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE,
                              related_name='observational_datasets')
    value = models.FloatField(help_text="Variable value")
    doi = models.CharField(max_length=512, help_text="DOI or URL for the dataset or time series")
    pr = models.FloatField(validators=PR_VALIDATOR,
                           help_text="Probability ratio")
    delta_i = models.FloatField(help_text="Change in intensity")
    comments = models.TextField(help_text="Remarks")

    class Meta:
        verbose_name = "observational dataset"


class ModelDataset(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE,
                              related_name='model_datasets')
    model_type = models.CharField(max_length=512,
                                  help_text="Statistical model applied to model data")
    period = models.CharField(max_length=128, help_text="Event return period")
    trend = models.CharField(max_length=512, help_text="Trend")
    pr = models.FloatField(validators=PR_VALIDATOR,
                           help_text="Probability ratio")
    delta_i = models.FloatField(help_text="Change in intensity")
