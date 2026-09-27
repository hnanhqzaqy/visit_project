from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path(
        'register/',
        views.register,
        name='register',
    ),

    path(
        'verify-phone/',
        views.verify_phone,
        name='verify_phone',
    ),

    path(
        'resend-register-code/',
        views.resend_register_code,
        name='resend_register_code',
    ),

    path(
        'login/',
        views.login_view,
        name='login',
    ),

    path(
        'forgot-password/',
        views.forgot_password,
        name='forgot_password',
    ),

    path(
        'verify-reset-code/',
        views.verify_reset_code,
        name='verify_reset_code',
    ),

    path(
        'resend-reset-code/',
        views.resend_reset_code,
        name='resend_reset_code',
    ),

    path(
        'reset-password/',
        views.reset_password,
        name='reset_password',
    ),
path('logout/', views.logout_view, name='logout'),
]