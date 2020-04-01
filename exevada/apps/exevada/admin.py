from django.contrib import admin
from . import models


@admin.register(models.Region)
class Region(admin.ModelAdmin):
    pass


class Impact(admin.StackedInline):
    model = models.Impact


class Synthesis(admin.StackedInline):
    models = models.Synthesis


class ObsDatasetInline(admin.StackedInline):
    model = models.ObsDataset
    extra = 1


#@admin.register(models.ModelDataset)
class ModelDatasetInline(admin.StackedInline):
    model = models.ModelDataset
    extra = 1


@admin.register(models.ObsDataset)
class ObsDataset(admin.ModelAdmin):
    pass


@admin.register(models.ModelDataset)
class ModelDataset(admin.ModelAdmin):
    pass


@admin.register(models.Impact)
class Impact(admin.ModelAdmin):
    pass



@admin.register(models.Synthesis)
class Synthesis(admin.ModelAdmin):
    pass


@admin.register(models.FitParameters)
class FitParameters(admin.ModelAdmin):
    pass


@admin.register(models.ReturnTime)
class ReturnTime(admin.ModelAdmin):
    pass


@admin.register(models.Event)
class Event(admin.ModelAdmin):
    inlines = [
        ObsDatasetInline,
        ModelDatasetInline
    ]
