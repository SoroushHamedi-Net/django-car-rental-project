from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    """
    مدل سفارشی کاربر با پشتیبانی از نقش‌های مدیر و مشتری،
    شماره تلفن یکتا و وضعیت اعتبارسنجی ایمیل و پیامک.
    """
    ROLE_CHOICES = (
        ('CUSTOMER', 'مشتری'),
        ('MANAGER', 'مدیر سامانه / ناوگان'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
        verbose_name='نقش کاربری',
        help_text='تعیین سطح دسترسی و نقش در سامانه'
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='شماره تماس',
        help_text='شماره همراه جهت دریافت پیامک و اعتبارسنجی OTP'
    )
    national_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='کد ملی',
        help_text='کد ملی ۱۰ رقمی جهت ثبت در قرارداد اجاره'
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='ایمیل تأیید شده',
        help_text='آیا ایمیل کاربر تایید شده است؟'
    )
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name='تلفن همراه تأیید شده',
        help_text='آیا شماره موبایل از طریق OTP تایید شده است؟'
    )

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        display_name = full_name if full_name else self.username
        return f"{display_name} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role == 'MANAGER' or self.is_superuser

    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'


class VerificationToken(models.Model):
    """
    توکن‌های موقت جهت اعتبارسنجی ایمیل و کد تایید پیامکی (OTP).
    """
    TOKEN_TYPES = (
        ('EMAIL', 'اعتبارسنجی ایمیل'),
        ('SMS', 'کد تایید پیامکی (OTP)'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='verification_tokens',
        verbose_name='کاربر'
    )
    token = models.CharField(
        max_length=64,
        verbose_name='توکن یا کد تایید'
    )
    token_type = models.CharField(
        max_length=10,
        choices=TOKEN_TYPES,
        verbose_name='نوع توکن'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ایجاد'
    )
    expires_at = models.DateTimeField(
        verbose_name='زمان انقضا'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='استفاده شده'
    )

    class Meta:
        verbose_name = 'توکن اعتبارسنجی'
        verbose_name_plural = 'توکن‌های اعتبارسنجی'
        ordering = ['-created_at']

    def __str__(self):
        return f"توکن {self.get_token_type_display()} برای {self.user.username}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # توکن پیامک ۱۰ دقیقه و توکن ایمیل ۲۴ ساعت اعتبار دارد
            if self.token_type == 'SMS':
                self.expires_at = timezone.now() + timedelta(minutes=10)
            else:
                self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
