from django.urls import path

from . import views


app_name = 'patient'


urlpatterns = [
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard',
    ),
    path(
        'profile/',
        views.profile,
        name='profile',
    ),
    path(
        'appointments/',
        views.my_appointments,
        name='appointments',
    ),
    path(
        'visit-history/',
        views.visit_history,
        name='visit_history',
    ),
    path(
        'visit/<int:appointment_id>/',
        views.visit_detail,
        name='visit_detail',
    ),
]