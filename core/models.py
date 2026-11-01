from django.db import models
from django.conf import settings


class NotificationLog(models.Model):
    """
    ثبت تاریخچه اعلان‌های ارسالی (ایمیل و شبیه‌سازی پیامک OTP / اطلاع‌رسانی) به کاربران و مدیران.
    """
    CHANNEL_CHOICES = (
        ('EMAIL', 'پست الکترونیکی (ایمیل)'),
        ('SMS', 'پیام کوتاه (SMS)'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='گیرنده پیام'
    )
    channel = models.CharField(
        max_length=10,
        choices=CHANNEL_CHOICES,
        default='SMS',
        verbose_name='کانال ارسال'
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='موضوع اعلان'
    )
    message = models.TextField(
        verbose_name='متن پیام'
    )
    is_sent = models.BooleanField(
        default=True,
        verbose_name='وضعیت ارسال موفق'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ارسال'
    )

    class Meta:
        verbose_name = 'گزارش اعلان'
        verbose_name_plural = 'گزارش اعلان‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"اعلان {self.get_channel_display()} به {self.recipient} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
