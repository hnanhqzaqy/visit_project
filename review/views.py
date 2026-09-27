from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from appointment.models import Appointment
from doctor.models import Doctor
from .forms import ReviewForm
from .models import Review
import jdatetime



@login_required
def create_review(request, appointment_id):
    if request.user.role != 'patient':
        messages.error(
            request,
            'فقط بیماران می‌توانند نظر ثبت کنند.',
        )
        return redirect('core:home')

    appointment = get_object_or_404(
        Appointment.objects.select_related('doctor', 'patient'),
        id=appointment_id,
        patient=request.user,
        status=Appointment.STATUS_COMPLETED,
    )

    if hasattr(appointment, 'review'):
        messages.warning(
            request,
            'برای این نوبت قبلاً نظر ثبت کرده‌اید.',
        )
        return redirect('patient:visit_history')

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()

            messages.success(
                request,
                'نظر شما با موفقیت ثبت شد.',
            )

            return redirect('patient:visit_history')

    else:
        form = ReviewForm()

    return render(
        request,
        'review/create.html',
        {
            'form': form,
            'appointment': appointment,
        },
    )


def doctor_reviews(request, doctor_id):
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
        'review/list.html',
        {
            'doctor': doctor,
            'reviews': reviews,
        },
    )