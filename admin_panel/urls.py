from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path(
        'users/',
        views.users,
        name='users',
    ),

    path(
        'doctors/',
        views.doctors,
        name='doctors',
    ),

    path(
        'doctors/<int:doctor_id>/status/',
        views.update_doctor_status,
        name='update_doctor_status',
    ),
    path(
        'patients/',
        views.patients,
        name='patients',
),
    path('appointments/', views.appointments, name='appointments'),
    path('visits/', views.visits, name='visits'),
    path('schedules/', views.schedules, name='schedules'),
    path('reviews/', views.reviews, name='reviews'),
]