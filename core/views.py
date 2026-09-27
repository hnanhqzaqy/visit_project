from django.db.models import Avg, Count, Q
from django.shortcuts import render

from doctor.models import Doctor


def home(request):
    search = request.GET.get('search', '').strip()

    doctors = Doctor.objects.filter(
        status=Doctor.STATUS_APPROVED
    )

    if search:
        doctors = doctors.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(specialty__icontains=search)
        )

    top_doctors = (
        doctors
        .annotate(
            average_rating=Avg(
                'appointments__review__rating'
            ),
            review_count=Count(
                'appointments__review'
            ),
        )
        .filter(
            review_count__gt=0
        )
        .order_by(
            '-average_rating',
            '-review_count',
            'last_name',
            'first_name',
        )[:6]
    )

    specialties = (
        Doctor.objects
        .filter(
            status=Doctor.STATUS_APPROVED
        )
        .values_list(
            'specialty',
            flat=True
        )
        .distinct()
        .order_by('specialty')
    )

    return render(
        request,
        'core/home.html',
        {
            'search': search,
            'top_doctors': top_doctors,
            'specialties': specialties,
        }
    )