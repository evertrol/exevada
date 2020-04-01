from django.urls import path, include


urlpatterns = [
    path('exevada/', include('apps.exevada.urls', namespace='events')),
]
