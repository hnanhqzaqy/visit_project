from django.urls import path

from . import views


app_name = 'doctor'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('list/', views.doctor_list, name='list'),
    path('<int:doctor_id>/', views.doctor_detail, name='detail'),

path(
    'schedule/',
    views.schedule_list,
    name='schedule_list'
),

path(
    'schedule/create/',
    views.schedule_create,
    name='schedule_create'
),

path(
    'schedule/<int:schedule_id>/edit/',
    views.schedule_update,
    name='schedule_update'
),

path(
    'schedule/<int:schedule_id>/delete/',
    views.schedule_delete,
    name='schedule_delete'
),
path(
    'appointments/',
    views.appointments,
    name='appointments',
),

path(
    'appointments/<int:appointment_id>/confirm/',
    views.confirm_appointment,
    name='confirm_appointment',
),

path(
    'appointments/<int:appointment_id>/cancel/',
    views.cancel_appointment,
    name='cancel_appointment',
),
path(
    'patients/',
    views.patients,
    name='patients',
),

path(
    'today-appointments/',
    views.today_appointments,
    name='today_appointments',
),

path(
    'patient-history/',
    views.patient_history,
    name='patient_history',
),
path(
    'visit/<int:appointment_id>/',
    views.visit_detail,
    name='visit_detail',
),
path(
    'reviews/',
    views.reviews,
    name='reviews'
),
]