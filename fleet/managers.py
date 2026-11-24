from django.apps import apps
from django.db import models


class CarQuerySet(models.QuerySet):
    """کوئری‌ست سفارشی برای فیلترهای پرکاربرد ناوگان خودروها."""

    def available(self):
        return self.filter(status='AVAILABLE')

    def in_maintenance(self):
        return self.filter(status='MAINTENANCE')

    def rented(self):
        return self.filter(status='RENTED')

    def by_price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None and min_price != '':
            qs = qs.filter(daily_price__gte=min_price)
        if max_price is not None and max_price != '':
            qs = qs.filter(daily_price__lte=max_price)
        return qs

    def available_for_dates(self, start_date, end_date):
        if not start_date or not end_date:
            return self
        RentalContract = apps.get_model('rentals', 'RentalContract')
        overlapping_car_ids = RentalContract.objects.filter(
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).values_list('car_id', flat=True)
        return self.exclude(id__in=overlapping_car_ids)


class CarManager(models.Manager):
    """منیجر سفارشی مدل خودرو جهت دسترسی یکپارچه به کوئری‌های دامنه."""

    def get_queryset(self):
        return CarQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def in_maintenance(self):
        return self.get_queryset().in_maintenance()

    def rented(self):
        return self.get_queryset().rented()

    def by_price_range(self, min_price=None, max_price=None):
        return self.get_queryset().by_price_range(min_price=min_price, max_price=max_price)

    def available_for_dates(self, start_date, end_date):
        return self.get_queryset().available_for_dates(start_date, end_date)
