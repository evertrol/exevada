from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from . import models


@admin.register(models.Region)
class Region(admin.ModelAdmin):
    pass

@admin.register(models.ObservationDataSet)
class ObservationDataSet(admin.ModelAdmin):
    pass

@admin.register(models.ModelDataSet)
class ModelDataSet(admin.ModelAdmin):
    pass

class JournalPaperInline(NestedStackedInline):
    model = models.JournalPaper
    extra = 0

class PressReleaseInline(NestedStackedInline):
    model = models.PressCommunication
    extra = 0

class ObservationAnalysisInline(NestedStackedInline):
    model = models.ObservationAnalysis
    extra = 1

class ModelAnalysisInline(NestedStackedInline):
    model = models.ModelAnalysis
    extra = 1

class AttributionInline(NestedStackedInline):
    model = models.Attribution
    extra = 1
    inlines = [ObservationAnalysisInline, ModelAnalysisInline, JournalPaperInline, PressReleaseInline]

@admin.register(models.Event)
class Event(NestedModelAdmin):
    inlines = [
        AttributionInline,
    ]
