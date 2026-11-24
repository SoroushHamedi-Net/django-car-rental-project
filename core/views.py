from django.shortcuts import render
from fleet.models import Car, CarBrand
from fleet.utils import get_recently_viewed_cars
from rentals.models import RentalContract
from fleet.forms import CarSearchFilterForm


def home_view(request):
    """
    نمای صفحه اصلی سامانه شامل بخش هیرو، جستجوی سریع، خودروهای منتخب،
    خودروهای اخیراً مشاهده‌شده و آمار کلیدی.
    """
    featured_cars = Car.objects.available().select_related('brand').order_by('-created_at')[:6]
    brands = CarBrand.objects.all()[:8]
    recently_viewed_cars = get_recently_viewed_cars(request)

    # آمار کلیدی سامانه
    total_cars_count = Car.objects.count()
    available_cars_count = Car.objects.available().count()
    total_rentals_count = RentalContract.objects.count()

    last_filters = request.session.get('last_search_filters', {})
    search_form = CarSearchFilterForm(initial=last_filters)

    context = {
        'featured_cars': featured_cars,
        'brands': brands,
        'recently_viewed_cars': recently_viewed_cars,
        'total_cars_count': total_cars_count,
        'available_cars_count': available_cars_count,
        'total_rentals_count': total_rentals_count,
        'search_form': search_form,
    }
    return render(request, 'core/home.html', context)
