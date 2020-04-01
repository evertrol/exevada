from django.urls import path
from . import views


app_name = 'exevada'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('event/', views.Events.as_view(), name='events'),
    path('event/<int:event_id>/', views.Event.as_view(), name='event'),
    path('event/<int:event_id>/obs-data/', views.ObsDatasets.as_view(), name='obsdata'),
    path('event/<int:event_id>/model-data/', views.ModelDatasets.as_view(), name='modeldata'),
    path('event/add/', views.CreateEvent.as_view(), name='add-event'),

    path('region/', views.Regions.as_view(), name='regions'),
    path('region/<int:region_id>/', views.Region.as_view(), name='region'),
    path('region/add/', views.CreateRegion.as_view(), name='add-region'),

]
