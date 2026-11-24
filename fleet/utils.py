from .models import Car


def get_recently_viewed_cars(request):
    """
    بازیابی خودروهای اخیراً مشاهده‌شده از سشن کاربر با حفظ ترتیب مشاهده (جدیدترین ابتدا).
    """
    car_ids = request.session.get('recently_viewed_cars', [])
    if not car_ids:
        return []

    cars_by_id = {
        car.pk: car
        for car in Car.objects.select_related('brand').filter(pk__in=car_ids)
    }
    return [cars_by_id[car_id] for car_id in car_ids if car_id in cars_by_id]
