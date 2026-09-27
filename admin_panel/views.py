from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
import jdatetime
from account.models import User
from doctor.models import Doctor, DoctorSchedule
from patient.models import Patient
from appointment.models import Appointment
from visit.models import Visit
from review.models import Review


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


@admin_required
def dashboard(request):
    return render(
        request,
        'admin_panel/dashboard.html',
    )


@admin_required
def users(request):
    users_list = User.objects.all().order_by('-date_joined')

    for user in users_list:
        user.jalali_date_joined = jdatetime.datetime.fromgregorian(
            datetime=user.date_joined
        ).strftime('%Y/%m/%d')

    return render(
        request,
        'admin_panel/users.html',
        {
            'users': users_list,
        }
    )


@admin_required
def doctors(request):
    doctors_list = (
        Doctor.objects
        .select_related('user')
        .prefetch_related('schedules')
        .order_by('-created_at')
    )

    return render(
        request,
        'admin_panel/doctors.html',
        {
            'doctors': doctors_list,
        }
    )


@admin_required
def update_doctor_status(request, doctor_id):
    if request.method != 'POST':
        raise PermissionDenied

    doctor = get_object_or_404(Doctor, id=doctor_id)

    status = request.POST.get('status')

    if status not in {
        Doctor.STATUS_APPROVED,
        Doctor.STATUS_REJECTED,
        Doctor.STATUS_PENDING,
    }:
        raise PermissionDenied

    doctor.status = status
    doctor.save(update_fields=['status', 'updated_at'])

    return redirect('admin_panel:doctors')


@admin_required
def patients(request):
    patients_list = (
        Patient.objects
        .select_related('user')
        .order_by('-created_at')
    )

    for patient in patients_list:
        patient.jalali_created_at = jdatetime.datetime.fromgregorian(
            datetime=patient.created_at
        ).strftime('%Y/%m/%d')

        if patient.birth_date:
            patient.jalali_birth_date = jdatetime.date.fromgregorian(
                date=patient.birth_date
            ).strftime('%Y/%m/%d')
        else:
            patient.jalali_birth_date = '—'

    return render(
        request,
        'admin_panel/patients.html',
        {
            'patients': patients_list,
        }
    )




@admin_required
def appointments(request):
    appointments_list = (
        Appointment.objects
        .select_related('doctor', 'patient')
        .order_by('-appointment_date', '-start_time')
    )

    for appointment in appointments_list:
        appointment.jalali_date = jdatetime.date.fromgregorian(
            date=appointment.appointment_date
        ).strftime('%Y/%m/%d')

    return render(
        request,
        'admin_panel/appointments.html',
        {
            'appointments': appointments_list,
        }
    )




@admin_required
def visits(request):
    visits_list = (
        Visit.objects
        .select_related(
            'appointment',
            'appointment__doctor',
            'appointment__patient',
        )
        .order_by('-created_at')
    )

    for visit in visits_list:
        visit.jalali_date = jdatetime.datetime.fromgregorian(
            datetime=visit.created_at
        ).strftime('%Y/%m/%d')

        visit.jalali_appointment_date = jdatetime.date.fromgregorian(
            date=visit.appointment.appointment_date
        ).strftime('%Y/%m/%d')

    return render(
        request,
        'admin_panel/visits.html',
        {
            'visits': visits_list,
        }
    )




@admin_required
def schedules(request):
    schedules_list = (
        DoctorSchedule.objects
        .select_related('doctor')
        .order_by('doctor__last_name', 'day_of_week', 'start_time')
    )

    return render(
        request,
        'admin_panel/schedules.html',
        {
            'schedules': schedules_list,
        }
    )




@admin_required
def reviews(request):
    reviews_list = (
        Review.objects
        .select_related(
            'appointment',
            'appointment__doctor',
            'appointment__patient',
        )
        .order_by('-created_at')
    )

    for review in reviews_list:
        review.jalali_date = jdatetime.datetime.fromgregorian(
            datetime=review.created_at
        ).strftime('%Y/%m/%d')

    return render(
        request,
        'admin_panel/reviews.html',
        {
            'reviews': reviews_list,
        }
    )