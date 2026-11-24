from django.db import models


class RentalContractQuerySet(models.QuerySet):
    """کوئری‌ست سفارشی برای قراردادها و درخواست‌های اجاره خودرو."""

    def pending_requests(self):
        return self.filter(status='PENDING')

    def active_contracts(self):
        return self.filter(status='APPROVED')

    def for_customer(self, user):
        return self.filter(customer=user)

    def overlapping(self, car, start_date, end_date, exclude_pk=None):
        qs = self.filter(
            car=car,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        return qs


class RentalContractManager(models.Manager):
    """منیجر سفارشی مدل قرارداد اجاره جهت ساده‌سازی پرس‌وجوهای تکراری."""

    def get_queryset(self):
        return RentalContractQuerySet(self.model, using=self._db)

    def pending_requests(self):
        return self.get_queryset().pending_requests()

    def active_contracts(self):
        return self.get_queryset().active_contracts()

    def for_customer(self, user):
        return self.get_queryset().for_customer(user)

    def overlapping(self, car, start_date, end_date, exclude_pk=None):
        return self.get_queryset().overlapping(
            car=car,
            start_date=start_date,
            end_date=end_date,
            exclude_pk=exclude_pk,
        )
