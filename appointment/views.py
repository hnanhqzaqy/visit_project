
from datetime import datetime, timedelta

import jdatetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from doctor.models import Doctor, DoctorSchedule

from .forms import AppointmentForm
from .models import Appointment, Payment


DAY_NAMES = {
    0: 'دوشنبه',
    1: 'سه‌شنبه',
    2: 'چهارشنبه',
    3: 'پنجشنبه',
    4: 'جمعه',
    5: 'شنبه',
    6: 'یکشنبه',
}


def get_available_slots_for_date(doctor, appointment_date):
    schedule = DoctorSchedule.objects.filter(
        doctor=doctor,
        day_of_week=appointment_date.weekday(),
        is_active=True,
    ).first()

    if not schedule:
        return []

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            payment_status__in=[
                Appointment.PAYMENT_PARTIAL,
                Appointment.PAYMENT_PAID,
            ],
        ).values_list(
            'start_time',
            flat=True,
        )
    )

    current_datetime = datetime.combine(
        appointment_date,
        schedule.start_time,
    )

    end_datetime = datetime.combine(
        appointment_date,
        schedule.end_time,
    )

    duration = timedelta(
        minutes=schedule.appointment_duration
    )

    slots = []

    while current_datetime + duration <= end_datetime:
        start_time = current_datetime.time()

        end_time = (
            current_datetime + duration
        ).time()

        if start_time not in booked_times:
            slots.append({
                'start': start_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M'),
            })

        current_datetime += duration

    return slots


@login_required
def create_appointment(request, doctor_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'فقط بیماران می‌توانند نوبت رزرو کنند.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        id=doctor_id,
        status=Doctor.STATUS_APPROVED,
    )

    if doctor.consultation_fee <= 0:
        messages.error(
            request,
            'هزینه ویزیت این پزشک هنوز تعیین نشده است.'
        )
        return redirect(
            'doctor:detail',
            doctor_id=doctor.id,
        )

    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment_date = form.cleaned_data[
                'appointment_date'
            ]

            start_time = form.cleaned_data[
                'start_time'
            ]

            schedule = DoctorSchedule.objects.filter(
                doctor=doctor,
                day_of_week=appointment_date.weekday(),
                is_active=True,
            ).first()

            if not schedule:
                form.add_error(
                    'appointment_date',
                    'پزشک در این روز برنامه کاری ندارد.'
                )

            else:
                today = timezone.localdate()

                if appointment_date < today:
                    form.add_error(
                        'appointment_date',
                        'امکان رزرو نوبت در گذشته وجود ندارد.'
                    )

                else:
                    start_datetime = datetime.combine(
                        appointment_date,
                        start_time,
                    )

                    end_datetime = (
                        start_datetime
                        + timedelta(
                            minutes=schedule.appointment_duration
                        )
                    )

                    end_time = end_datetime.time()

                    if start_time < schedule.start_time:
                        form.add_error(
                            'start_time',
                            'این ساعت قبل از شروع برنامه کاری پزشک است.'
                        )

                    elif start_time >= schedule.end_time:
                        form.add_error(
                            'start_time',
                            'این ساعت خارج از برنامه کاری پزشک است.'
                        )

                    elif end_time > schedule.end_time:
                        form.add_error(
                            'start_time',
                            'مدت این نوبت از ساعات کاری پزشک خارج می‌شود.'
                        )

                    else:
                        existing_appointment = (
                            Appointment.objects.filter(
                                doctor=doctor,
                                appointment_date=appointment_date,
                                start_time=start_time,
                                payment_status__in=[
                                    Appointment.PAYMENT_PARTIAL,
                                    Appointment.PAYMENT_PAID,
                                ],
                            ).exists()
                        )

                        if existing_appointment:
                            form.add_error(
                                'start_time',
                                'این زمان قبلاً رزرو شده است.'
                            )

                        else:
                            appointment = form.save(
                                commit=False
                            )

                            appointment.doctor = doctor
                            appointment.patient = request.user
                            appointment.end_time = end_time

                            appointment.status = (
                                Appointment.STATUS_PENDING
                            )

                            # ذخیره اطلاعات مالی نوبت
                            appointment.payment_policy = (
                                doctor.payment_policy
                            )

                            appointment.total_amount = (
                                doctor.consultation_fee
                            )

                            if (
                                doctor.payment_policy
                                == Doctor.PAYMENT_FULL
                            ):
                                appointment.payable_amount = (
                                    doctor.consultation_fee
                                )

                                appointment.remaining_amount = 0

                            elif (
                                doctor.payment_policy
                                == Doctor.PAYMENT_DEPOSIT
                            ):
                                appointment.payable_amount = (
                                    doctor.consultation_fee * 30
                                ) // 100

                                appointment.remaining_amount = (
                                    doctor.consultation_fee
                                    - appointment.payable_amount
                                )

                            appointment.paid_amount = 0

                            appointment.payment_status = (
                                Appointment.PAYMENT_PENDING
                            )

                            appointment.save()

                            return redirect(
                                'appointment:payment',
                                appointment_id=appointment.id,
                            )

    else:
        form = AppointmentForm()

    return render(
        request,
        'appointment/create.html',
        {
            'form': form,
            'doctor': doctor,
        },
    )


@login_required
def payment(request, appointment_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'فقط بیماران می‌توانند وارد بخش پرداخت شوند.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects.select_related('doctor'),
        id=appointment_id,
        patient=request.user,
    )

    if appointment.status == Appointment.STATUS_CANCELLED:
        messages.error(
            request,
            'این نوبت لغو شده است و امکان پرداخت آن وجود ندارد.'
        )
        return redirect('patient:appointments')

    if appointment.payment_status == Appointment.PAYMENT_PAID:
        messages.info(
            request,
            'هزینه این نوبت قبلاً به طور کامل پرداخت شده است.'
        )
        return redirect('patient:appointments')

    if appointment.payable_amount <= 0:
        messages.error(
            request,
            'مبلغ قابل پرداخت معتبر نیست.'
        )
        return redirect('patient:appointments')

    if request.method == 'POST':
        messages.warning(
            request,
            'درگاه پرداخت آنلاین در حال حاضر فعال نیست. '
            'پس از راه‌اندازی درگاه، امکان پرداخت فراهم خواهد شد.'
        )

        return redirect(
            'appointment:payment',
            appointment_id=appointment.id,
        )

    return render(
        request,
        'appointment/payment.html',
        {
            'appointment': appointment,
        },
    )


@login_required
def payment_receipt(request, appointment_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'فقط بیماران می‌توانند رسید پرداخت را مشاهده کنند.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'doctor',
            'patient',
            'patient__patient_profile',
        ),
        id=appointment_id,
        patient=request.user,
    )

    payment_record = (
        Payment.objects
        .filter(
            appointment=appointment,
            status=Payment.STATUS_SUCCESS,
        )
        .order_by('-paid_at', '-created_at')
        .first()
    )

    if payment_record is None:
        messages.error(
            request,
            'برای این نوبت رسید پرداخت تأییدشده‌ای وجود ندارد.'
        )
        return redirect('patient:appointments')

    jalali_date = jdatetime.date.fromgregorian(
        date=appointment.appointment_date
    )

    appointment.jalali_date = jalali_date.strftime(
        '%Y/%m/%d'
    )

    return render(
        request,
        'appointment/payment_receipt.html',
        {
            'appointment': appointment,
            'payment': payment_record,
        }
    )


@login_required
def weekly_available_slots(request, doctor_id):
    if request.user.role != 'patient':
        return JsonResponse(
            {
                'success': False,
                'message': 'دسترسی غیرمجاز.',
            },
            status=403,
        )

    doctor = get_object_or_404(
        Doctor,
        id=doctor_id,
        status=Doctor.STATUS_APPROVED,
    )

    today = timezone.localdate()

    days = []

    for day_offset in range(7):
        current_date = today + timedelta(
            days=day_offset
        )

        jalali_date = jdatetime.date.fromgregorian(
            date=current_date
        )

        slots = get_available_slots_for_date(
            doctor,
            current_date,
        )

        days.append({
            'gregorian_date': current_date.isoformat(),
            'jalali_date': jalali_date.strftime(
                '%Y/%m/%d'
            ),
            'day_name': DAY_NAMES[
                current_date.weekday()
            ],
            'is_today': day_offset == 0,
            'slots': slots,
        })

    return JsonResponse({
        'success': True,
        'days': days,
    })


@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'فقط بیماران می‌توانند نوبت خود را لغو کنند.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user,
    )

    if appointment.status == Appointment.STATUS_CANCELLED:
        messages.warning(
            request,
            'این نوبت قبلاً لغو شده است.'
        )
        return redirect('patient:appointments')

    # بعد از پرداخت، لغو و بازگشت وجه امکان‌پذیر نیست.
    if appointment.payment_status in [
        Appointment.PAYMENT_PARTIAL,
        Appointment.PAYMENT_PAID,
    ]:
        messages.error(
            request,
            'پس از پرداخت، امکان لغو نوبت و بازگشت وجه وجود ندارد.'
        )
        return redirect('patient:appointments')

    if appointment.status != Appointment.STATUS_PENDING:
        messages.error(
            request,
            'این نوبت در وضعیت قابل لغو قرار ندارد.'
        )
        return redirect('patient:appointments')

    appointment.status = Appointment.STATUS_CANCELLED

    appointment.save(
        update_fields=['status', 'updated_at']
    )

    messages.success(
        request,
        'نوبت شما با موفقیت لغو شد.'
    )

    return redirect('patient:appointments')
