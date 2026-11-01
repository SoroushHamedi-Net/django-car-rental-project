from django.db import models
from django.conf import settings


class CarBrand(models.Model):
    """
    برندهای خودروسازی (مانند بنز، ب‌ام‌و، هیوندای، تویوتا، پژو).
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام برند'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='کشور سازنده'
    )
    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        verbose_name='لوگوی برند'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    class Meta:
        verbose_name = 'برند خودرو'
        verbose_name_plural = 'برندهای خودرو'
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):
    """
    مدل اصلی ناوگان خودرو با قابلیت تعیین وضعیت فیزیکی و موقعیت جغرافیایی تحویل بر روی نقشه.
    """
    STATUS_CHOICES = (
        ('AVAILABLE', 'قابل اجاره'),
        ('MAINTENANCE', 'در دست تعمیر یا چک وضعیت'),
        ('RENTED', 'اجاره شده'),
    )

    brand = models.ForeignKey(
        CarBrand,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='برند سازنده'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='مدل خودرو'
    )
    year = models.PositiveIntegerField(
        verbose_name='سال ساخت (شمسی یا میلادی)'
    )
    daily_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت اجاره روزانه (تومان)',
        help_text='نرخ پایه کرایه برای هر ۲۴ ساعت به تومان'
    )
    capacity = models.PositiveSmallIntegerField(
        default=4,
        verbose_name='ظرفیت سرنشین (نفر)'
    )
    features = models.TextField(
        blank=True,
        verbose_name='امکانات و آپشن‌ها',
        help_text='مثال: گیربکس اتوماتیک، سانروف، سیستم صوتی حرفه‌ای، بیمه طلایی کامل'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE',
        verbose_name='وضعیت خودرو'
    )
    pickup_address = models.CharField(
        max_length=255,
        default='تهران، میدان آزادی، دفتر مرکزی سامانه',
        verbose_name='آدرس محل تحویل خودرو'
    )
    latitude = models.FloatField(
        default=35.6892,
        verbose_name='عرض جغرافیایی (Latitude)',
        help_text='مختصات جهت نمایش موقعیت بر روی نقشه Leaflet'
    )
    longitude = models.FloatField(
        default=51.3890,
        verbose_name='طول جغرافیایی (Longitude)',
        help_text='مختصات جهت نمایش موقعیت بر روی نقشه Leaflet'
    )
    image = models.ImageField(
        upload_to='cars/',
        blank=True,
        null=True,
        verbose_name='تصویر شاخص خودرو'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registered_cars',
        verbose_name='ثبت‌کننده (مدیر)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ افزودن به ناوگان'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ آخرین ویرایش'
    )

    class Meta:
        verbose_name = 'خودرو'
        verbose_name_plural = 'ناوگان خودروها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} {self.model_name} ({self.year}) - {self.get_status_display()}"

    @property
    def is_available(self):
        return self.status == 'AVAILABLE'
