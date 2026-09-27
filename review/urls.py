from django.urls import path

from . import views


app_name = 'review'


urlpatterns = [
    path(
        'create/<int:appointment_id>/',
        views.create_review,
        name='create',
    ),
    path(
        'doctor/<int:doctor_id>/',
        views.doctor_reviews,
        name='doctor_reviews',
    ),
]