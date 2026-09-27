from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from appointment.models import Appointment
from .forms import VisitForm


@login_required
def create_visit(request, appointment_id):

    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به ثبت ویزیت ندارید.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'doctor',
            'patient',
        ),
        id=appointment_id,
        doctor__user=request.user,
    )

    if appointment.status != Appointment.STATUS_CONFIRMED:
        messages.warning(
            request,
            'فقط برای نوبت‌های تأییدشده می‌توانید ویزیت ثبت کنید.'
        )
        return redirect('doctor:appointments')

    if hasattr(appointment, 'visit'):
        messages.warning(
            request,
            'برای این نوبت قبلاً ویزیت ثبت شده است.'
        )
        return redirect('doctor:appointments')

    if request.method == 'POST':

        form = VisitForm(request.POST)

        if form.is_valid():

            visit = form.save(commit=False)
            visit.appointment = appointment
            visit.save()

            appointment.status = Appointment.STATUS_COMPLETED
            appointment.save(
                update_fields=[
                    'status',
                    'updated_at',
                ]
            )

            messages.success(
                request,
                'ویزیت بیمار با موفقیت ثبت شد.'
            )

            return redirect('doctor:appointments')

    else:
        form = VisitForm()

    return render(
        request,
        'visit/create.html',
        {
            'form': form,
            'appointment': appointment,
        },
    )