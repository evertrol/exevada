from django.urls import path
from . import views


app_name = 'exevada'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('events/', views.EventsView.as_view(), name='events'),
    path('events/<int:event_id>/', views.EventView.as_view(), name='event'),
    path('attributions/', views.AttributionsView.as_view(), name='attributions'),
    path('attributions/<int:attribution_id>/', views.AttributionView.as_view(), name='attribution'),
    path('obsdata/', views.ObsDatasets.as_view(), name='observation'),
    path('moddata/', views.ModDatasets.as_view(), name='simulation'),
]
