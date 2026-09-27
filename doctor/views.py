from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from account.models import User
from .forms import (
    DoctorProfileForm,
    DoctorRegisterForm,
    DoctorScheduleForm,
)
from .models import Doctor, DoctorSchedule
import jdatetime
from appointment.models import Appointment
from django.utils import timezone
from visit.models import Visit
from django.db.models import Avg, Count
from review.models import Review



@login_required
def dashboard(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor, created = Doctor.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': '',
            'last_name': '',
            'medical_system_number': f'TEMP-{request.user.id}',
            'specialty': 'ثبت نشده',
        }
    )

    return render(
        request,
        'doctor/dashboard.html',
        {
            'doctor': doctor,
        }
    )

@login_required
def reviews(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user,
    )

    review_stats = Review.objects.filter(
        appointment__doctor=doctor,
    ).aggregate(
        average_rating=Avg('rating'),
        review_count=Count(
            'id',
            distinct=True,
        ),
    )

    reviews = (
        Review.objects
        .filter(
            appointment__doctor=doctor,
        )
        .order_by('-created_at')
    )

    for review in reviews:
        jalali_date = jdatetime.date.fromgregorian(
            date=review.created_at.date()
        )

        review.jalali_date = jalali_date.strftime(
            '%Y/%m/%d'
        )

    return render(
        request,
        'doctor/reviews.html',
        {
            'doctor': doctor,
            'reviews': reviews,
            'average_rating': review_stats['average_rating'],
            'review_count': review_stats['review_count'],
        }
    )

@login_required
def profile(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor, created = Doctor.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': '',
            'last_name': '',
            'medical_system_number': f'TEMP-{request.user.id}',
            'specialty': 'ثبت نشده',
        }
    )

    if request.method == 'POST':
        form = DoctorProfileForm(
            request.POST,
            request.FILES,
            instance=doctor,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'اطلاعات پروفایل پزشک با موفقیت ذخیره شد.'
            )

            return redirect('doctor:profile')

    else:
        form = DoctorProfileForm(instance=doctor)

    return render(
        request,
        'doctor/profile.html',
        {
            'form': form,
            'doctor': doctor,
        }
    )
@login_required
def schedule_list(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    schedules = doctor.schedules.all()

    return render(
        request,
        'doctor/schedule_list.html',
        {
            'doctor': doctor,
            'schedules': schedules,
        }
    )


@login_required
def schedule_create(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    if doctor.status != Doctor.STATUS_APPROVED:
        messages.warning(
            request,
            'تا زمانی که حساب شما توسط مدیر تأیید نشود، امکان تنظیم برنامه کاری وجود ندارد.'
        )
        return redirect('doctor:dashboard')

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)

        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.doctor = doctor
            schedule.save()

            messages.success(
                request,
                'برنامه کاری با موفقیت اضافه شد.'
            )

            return redirect('doctor:schedule_list')

    else:
        form = DoctorScheduleForm()

    return render(
        request,
        'doctor/schedule_form.html',
        {
            'form': form,
            'doctor': doctor,
            'page_title': 'افزودن برنامه کاری',
        }
    )

@login_required
def schedule_update(request, schedule_id):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    schedule = get_object_or_404(
        DoctorSchedule,
        id=schedule_id,
        doctor=doctor
    )

    if doctor.status != Doctor.STATUS_APPROVED:
        messages.warning(
            request,
            'حساب شما هنوز توسط مدیر تأیید نشده است.'
        )
        return redirect('doctor:dashboard')

    if request.method == 'POST':
        form = DoctorScheduleForm(
            request.POST,
            instance=schedule
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'برنامه کاری با موفقیت ویرایش شد.'
            )

            return redirect('doctor:schedule_list')

    else:
        form = DoctorScheduleForm(instance=schedule)

    return render(
        request,
        'doctor/schedule_form.html',
        {
            'form': form,
            'doctor': doctor,
            'page_title': 'ویرایش برنامه کاری',
        }
    )

@login_required
@require_POST
def schedule_delete(request, schedule_id):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    schedule = get_object_or_404(
        DoctorSchedule,
        id=schedule_id,
        doctor=doctor,
    )

    schedule.delete()

    messages.success(
        request,
        'برنامه کاری با موفقیت حذف شد.'
    )

    return redirect('doctor:schedule_list')

def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password'],
                role=User.ROLE_DOCTOR,
                is_active=True,
            )

            Doctor.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                medical_system_number=form.cleaned_data[
                    'medical_system_number'
                ],
                specialty=form.cleaned_data['specialty'],
                experience_years=form.cleaned_data[
                    'experience_years'
                ],
                bio=form.cleaned_data['bio'],
                clinic_address=form.cleaned_data[
                    'clinic_address'
                ],
            )

            login(request, user)

            messages.success(
                request,
                'درخواست ثبت‌نام شما با موفقیت ثبت شد و در انتظار بررسی مدیر است.'
            )

            return redirect('doctor:dashboard')

    else:
        form = DoctorRegisterForm()

    return render(
        request,
        'doctor/register.html',
        {
            'form': form,
        }
    )

def doctor_list(request):
    doctors = Doctor.objects.filter(
        status=Doctor.STATUS_APPROVED
    )

    search = request.GET.get('search', '').strip()

    if search:
        doctors = doctors.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(specialty__icontains=search)
        )

    doctors = doctors.order_by('last_name', 'first_name')

    return render(
        request,
        'doctor/list.html',
        {
            'doctors': doctors,
            'search': search,
        }
    )

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(
        Doctor.objects.annotate(
            average_rating=Avg(
                'appointments__review__rating'
            ),
            review_count=Count(
                'appointments__review',
                distinct=True,
            ),
        ),
        id=doctor_id,
        status=Doctor.STATUS_APPROVED,
    )

    reviews = (
        Review.objects
        .filter(
            appointment__doctor=doctor,
        )
        .select_related(
            'appointment',
        )
        .order_by('-created_at')[:5]
    )

    return render(
        request,
        'doctor/detail.html',
        {
            'doctor': doctor,
            'reviews': reviews,
        }
    )
@login_required
def appointments(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    appointments = (
        Appointment.objects
        .filter(
            doctor=doctor,
            payment_status__in=[
                Appointment.PAYMENT_PARTIAL,
                Appointment.PAYMENT_PAID,
            ],
        )
        .select_related(
            'patient',
            'patient__patient_profile',
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
        'doctor/appointments.html',
        {
            'doctor': doctor,
            'appointments': appointments,
        }
    )
@login_required
@require_POST
def confirm_appointment(request, appointment_id):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if appointment.status != Appointment.STATUS_PENDING:
        messages.warning(
            request,
            'این نوبت در وضعیت قابل تأیید قرار ندارد.'
        )
        return redirect('doctor:appointments')

    if appointment.payment_status not in [
        Appointment.PAYMENT_PARTIAL,
        Appointment.PAYMENT_PAID,
    ]:
        messages.error(
            request,
            'این نوبت هنوز پرداخت نشده است و امکان تأیید آن وجود ندارد.'
        )
        return redirect('doctor:appointments')

    appointment.status = Appointment.STATUS_CONFIRMED

    appointment.save(
        update_fields=['status', 'updated_at']
    )

    messages.success(
        request,
        'نوبت با موفقیت تأیید شد.'
    )

    return redirect('doctor:appointments')
@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if appointment.status in [
        Appointment.STATUS_CANCELLED,
        Appointment.STATUS_COMPLETED,
    ]:
        messages.warning(
            request,
            'این نوبت قابل لغو نیست.'
        )
        return redirect('doctor:appointments')

    # بعد از پرداخت، لغو نوبت و بازگشت وجه امکان‌پذیر نیست.
    if appointment.payment_status in [
        Appointment.PAYMENT_PARTIAL,
        Appointment.PAYMENT_PAID,
    ]:
        messages.error(
            request,
            'این نوبت پرداخت شده است و امکان لغو آن وجود ندارد.'
        )
        return redirect('doctor:appointments')

    appointment.status = Appointment.STATUS_CANCELLED

    appointment.save(
        update_fields=['status', 'updated_at']
    )

    messages.success(
        request,
        'نوبت با موفقیت لغو شد.'
    )

    return redirect('doctor:appointments')
@login_required
def patients(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    patient_ids = (
        Appointment.objects
        .filter(doctor=doctor)
        .values_list('patient_id', flat=True)
        .distinct()
    )

    patients = (
        User.objects
        .filter(
            id__in=patient_ids,
            role=User.ROLE_PATIENT,
        )
        .select_related('patient_profile')
        .order_by('phone')
    )

    return render(
        request,
        'doctor/patients.html',
        {
            'doctor': doctor,
            'patients': patients,
        }
    )
@login_required
def today_appointments(request):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    today = timezone.localdate()

    appointments = (
        Appointment.objects
        .filter(
            doctor=doctor,
            appointment_date=today,
        )
        .select_related(
            'patient',
            'patient__patient_profile',
        )
        .order_by('start_time')
    )

    jalali_date = jdatetime.date.fromgregorian(
        date=today
    ).strftime('%Y/%m/%d')

    for appointment in appointments:
        appointment.patient_name = (
            f'{appointment.patient.patient_profile.first_name} '
            f'{appointment.patient.patient_profile.last_name}'
        ).strip()

    return render(
        request,
        'doctor/today_appointments.html',
        {
            'doctor': doctor,
            'appointments': appointments,
            'jalali_date': jalali_date,
        }
    )

@login_required
def patient_history(request):
    if request.user.role != 'doctor':
        messages.error(request, 'شما دسترسی به بخش پزشکان ندارید.')
        return redirect('core:home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user,
    )

    appointments = (
        Appointment.objects
        .filter(
            doctor=doctor,
            status=Appointment.STATUS_COMPLETED,
        )
        .select_related(
            'patient',
            'patient__patient_profile',
        )
        .prefetch_related(
            'visit',
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

        appointment.patient_name = (
            f'{appointment.patient.patient_profile.first_name} '
            f'{appointment.patient.patient_profile.last_name}'
        ).strip()

    return render(
        request,
        'doctor/patient_history.html',
        {
            'doctor': doctor,
            'appointments': appointments,
        }
    )


@login_required
def visit_detail(request, appointment_id):
    if request.user.role != 'doctor':
        messages.error(
            request,
            'شما دسترسی به بخش پزشکان ندارید.'
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects
        .select_related(
            'doctor',
            'patient',
            'patient__patient_profile',
        ),
        id=appointment_id,
        doctor__user=request.user,
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
        'doctor/visit_detail.html',
        {
            'appointment': appointment,
            'visit': visit,
        }
    )