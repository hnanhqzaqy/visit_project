from django.urls import path

from . import views


app_name = 'visit'


urlpatterns = [
    path(
        'create/<int:appointment_id>/',
        views.create_visit,
        name='create',
    ),
]