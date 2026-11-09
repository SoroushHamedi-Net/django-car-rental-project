from django.shortcuts import render
from fleet.models import Car, CarBrand
from rentals.models import RentalContract
from fleet.forms import CarSearchFilterForm


def home_view(request):
    """
    نمای صفحه اصلی سامانه شامل بخش هیرو، جستجوی سریع، خودروهای منتخب و آمار کلیدی.
    """
    featured_cars = Car.objects.filter(status='AVAILABLE').select_related('brand').order_by('-created_at')[:6]
    brands = CarBrand.objects.all()[:8]

    # آمار کلیدی سامانه
    total_cars_count = Car.objects.count()
    available_cars_count = Car.objects.filter(status='AVAILABLE').count()
    total_rentals_count = RentalContract.objects.count()

    search_form = CarSearchFilterForm()

    context = {
        'featured_cars': featured_cars,
        'brands': brands,
        'total_cars_count': total_cars_count,
        'available_cars_count': available_cars_count,
        'total_rentals_count': total_rentals_count,
        'search_form': search_form,
    }
    return render(request, 'core/home.html', context)
