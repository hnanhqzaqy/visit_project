from .forms import PatientProfileForm
from .models import Patient
from appointment.models import Appointment
import jdatetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from visit.models import Visit




@login_required
def dashboard(request):
    if request.user.role != 'patient':
        messages.error(
            request,
            'شما دسترسی به بخش بیماران ندارید.'
        )
        return redirect('core:home')

    patient, created = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': '',
            'last_name': '',
        }
    )

    jalali_birth_date = None

    if patient.birth_date:
        jalali_date = jdatetime.date.fromgregorian(
            date=patient.birth_date
        )

        jalali_birth_date = jalali_date.strftime('%Y/%m/%d')

    jalali_joined_date = None

    if request.user.date_joined:
        jalali_joined = jdatetime.datetime.fromgregorian(
            datetime=request.user.date_joined
        )

        jalali_joined_date = jalali_joined.strftime('%Y/%m/%d')

    return render(
        request,
        'patient/dashboard.html',
        {
            'patient': patient,
            'jalali_birth_date': jalali_birth_date,
            'jalali_joined_date': jalali_joined_date,
        }
    )


@login_required
def profile(request):
    if request.user.role != 'patient':
        messages.error(
            request,
            'شما دسترسی به بخش بیماران ندارید.'
        )
        return redirect('core:home')

    patient, created = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': '',
            'last_name': '',
        }
    )

    if request.method == 'POST':
        form = PatientProfileForm(
            request.POST,
            request.FILES,
            instance=patient,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'اطلاعات پروفایل با موفقیت ذخیره شد.'
            )

            return redirect('patient:profile')

    else:
        form = PatientProfileForm(instance=patient)

    return render(
        request,
        'patient/profile.html',
        {
            'form': form,
            'patient': patient,
        }
    )




@login_required
def my_appointments(request):
    if request.user.role != 'patient':
        messages.error(
            request,
            'شما دسترسی به بخش بیماران ندارید.'
        )
        return redirect('core:home')

    appointments = (
        Appointment.objects
        .filter(
            patient=request.user,
            payment_status__in=[
                Appointment.PAYMENT_PARTIAL,
                Appointment.PAYMENT_PAID,
            ],
        )
        .select_related('doctor')
        .order_by(
            '-appointment_date',
            '-start_time',
        )
    )

    for appointment in appointments:
        jalali_date = jdatetime.date.fromgregorian(
            date=appointment.appointment_date
        )

        appointment.jalali_date = jalali_date.strftime(
            '%Y/%m/%d'
        )

    return render(
        request,
        'patient/appointments.html',
        {
            'appointments': appointments,
        },
    )


@login_required
def visit_history(request):
    if request.user.role != 'patient':
        messages.error(
            request,
            'شما دسترسی به بخش بیماران ندارید.'
        )
        return redirect('core:home')

    appointments = (
        Appointment.objects
        .filter(
            patient=request.user,
            status=Appointment.STATUS_COMPLETED,
        )
        .select_related(
            'doctor',
        )
        .prefetch_related(
            'visit',
            'review',
        )
        .order_by(
            '-appointment_date',
            '-start_time',
        )
    )

    for appointment in appointments:
        jalali_date = jdatetime.date.fromgregorian(
            date=appointment.appointment_date
        )

        appointment.jalali_date = jalali_date.strftime(
            '%Y/%m/%d'
        )

    return render(
        request,
        'patient/visit_history.html',
        {
            'appointments': appointments,
        }
    )







@login_required
def visit_detail(request, appointment_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'شما دسترسی به بخش بیماران ندارید.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'doctor',
            'patient',
        ),
        id=appointment_id,
        patient=request.user,
        status=Appointment.STATUS_COMPLETED,
    )

    visit = get_object_or_404(
        Visit,
        appointment=appointment,
    )

    jalali_date = jdatetime.date.fromgregorian(
        date=appointment.appointment_date
    )

    appointment.jalali_date = jalali_date.strftime(
        '%Y/%m/%d'
    )

    return render(
        request,
        'patient/visit_detail.html',
        {
            'appointment': appointment,
            'visit': visit,
        }
    )