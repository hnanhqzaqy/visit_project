from django.urls import path

from . import views


app_name = 'appointment'


urlpatterns = [
    path(
        'doctor/<int:doctor_id>/book/',
        views.create_appointment,
        name='create',
    ),

    path(
        'doctor/<int:doctor_id>/weekly-slots/',
        views.weekly_available_slots,
        name='weekly_slots',
    ),

    path(
        '<int:appointment_id>/cancel/',
        views.cancel_appointment,
        name='cancel',
    ),

    path(
        '<int:appointment_id>/payment/',
        views.payment,
        name='payment',
    ),

    path(
        'payment/<int:appointment_id>/receipt/',
        views.payment_receipt,
        name='payment_receipt',
    ),
]