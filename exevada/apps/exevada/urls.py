from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('events/', views.EventsView.as_view(), name='events'),
    path('events/<int:pk>/', views.EventView.as_view(), name='event'),
    path('attributions/', views.AttributionsView.as_view(), name='attributions'),
    path('attributions/<int:pk>/', views.AttributionView.as_view(), name='attribution'),
    path('obsdata/', views.ObsDatasets.as_view(), name='observation'),
    path('moddata/', views.ModDatasets.as_view(), name='simulation'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)