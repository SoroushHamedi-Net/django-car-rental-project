import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from fleet.models import Car


class RentalContract(models.Model):
    """
    قرارداد و درخواست اجاره خودرو شامل اعتبارسنجی تداخل تاریخی،
    گردش‌کار تایید/رد مدیر، و ذخیره نرخ اسنپ‌شات مالی.
    """
    STATUS_CHOICES = (
        ('PENDING', 'در انتظار بررسی مدیر'),
        ('APPROVED', 'تأیید شده / قرارداد فعال'),
        ('REJECTED', 'رد شده توسط مدیر'),
        ('CANCELLED', 'لغو شده توسط مشتری'),
        ('COMPLETED', 'تحویل داده شده / پایان یافته'),
    )

    contract_code = models.CharField(
        max_length=24,
        unique=True,
        editable=False,
        verbose_name='کد پیگیری قرارداد'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rentals',
        verbose_name='مشتری'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='rental_contracts',
        verbose_name='خودرو مورد اجاره'
    )
    start_date = models.DateField(
        verbose_name='تاریخ شروع اجاره'
    )
    end_date = models.DateField(
        verbose_name='تاریخ پایان اجاره'
    )
    daily_rate_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='نرخ روزانه در زمان عقد (تومان)',
        help_text='ثبت قطعی قیمت روزانه در زمان درخواست جهت ثبات مالی قرارداد'
    )
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        verbose_name='مبلغ کل قرارداد (تومان)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='وضعیت قرارداد'
    )
    manager_note = models.TextField(
        blank=True,
        verbose_name='یادداشت مدیر',
        help_text='توضیحات تکمیلی یا علت تایید/رد درخواست توسط مدیر'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_contracts',
        verbose_name='بررسی‌کننده (مدیر)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ثبت درخواست'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='زمان آخرین تغییر'
    )

    class Meta:
        verbose_name = 'قرارداد اجاره'
        verbose_name_plural = 'قراردادهای اجاره'
        ordering = ['-created_at']

    def __str__(self):
        return f"قرارداد {self.contract_code} - {self.car} ({self.get_status_display()})"

    @property
    def total_days(self):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days
            return max(delta, 1)
        return 1

    def clean(self):
        """
        اعتبارسنجی در سطح مدل برای جلوگیری از تناقض تاریخ‌ها و هم‌پوشانی رزرواسیون‌ها.
        """
        super().clean()
        today = timezone.localdate()

        if self.start_date and self.start_date < today and not self.pk:
            raise ValidationError({'start_date': 'تاریخ شروع نمی‌تواند در گذشته باشد.'})

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({'end_date': 'تاریخ پایان اجاره باید بعد از تاریخ شروع باشد.'})

            # بررسی تداخل زمانی با سایر قراردادهای فعال یا تایید شده برای همین خودرو
            overlapping_contracts = RentalContract.objects.filter(
                car=self.car,
                status__in=['PENDING', 'APPROVED'],
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            )

            if self.pk:
                overlapping_contracts = overlapping_contracts.exclude(pk=self.pk)

            if overlapping_contracts.exists():
                raise ValidationError(
                    'این خودرو در بازه زمانی انتخابی قبلاً رزرو شده است یا در حال بررسی می‌باشد. لطفاً تاریخ‌های دیگری انتخاب کنید.'
                )

    def save(self, *args, **kwargs):
        # تولید کد یکتای قرارداد در صورت عدم وجود
        if not self.contract_code:
            short_id = uuid.uuid4().hex[:8].upper()
            self.contract_code = f"CR-{short_id}"

        # محاسبه خودکار نرخ اسنپ‌شات و مبلغ کل بر اساس تعداد روزها
        if self.car and not self.daily_rate_snapshot:
            self.daily_rate_snapshot = self.car.daily_price

        if self.start_date and self.end_date and self.daily_rate_snapshot:
            days = (self.end_date - self.start_date).days
            self.total_price = max(days, 1) * self.daily_rate_snapshot

        super().save(*args, **kwargs)
