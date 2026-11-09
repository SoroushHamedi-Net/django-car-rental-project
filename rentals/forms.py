from django import forms
from django.utils import timezone
from .models import RentalContract


class RentalRequestForm(forms.ModelForm):
    """
    فرم ثبت درخواست اجاره خودرو توسط مشتری با تعیین تاریخ‌های شروع و پایان.
    """
    class Meta:
        model = RentalContract
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'start_date': 'تاریخ شروع اجاره (تحویل)',
            'end_date': 'تاریخ پایان اجاره (عودت)',
        }

    def __init__(self, *args, car=None, **kwargs):
        self.car = car
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = timezone.localdate()

        if start_date and start_date < today:
            self.add_error('start_date', 'تاریخ شروع نمی‌تواند در گذشته باشد.')

        if start_date and end_date:
            if end_date <= start_date:
                self.add_error('end_date', 'تاریخ پایان اجاره باید حداقل یک روز بعد از تاریخ شروع باشد.')

            if self.car:
                # بررسی هم‌پوشانی تاریخی با قراردادهای تأیید شده یا در حال بررسی دیگر
                overlapping = RentalContract.objects.filter(
                    car=self.car,
                    status__in=['PENDING', 'APPROVED'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                if self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    raise forms.ValidationError(
                        'این خودرو در بازه زمانی انتخابی قبلاً رزرو شده است یا در حال بررسی می‌باشد. لطفاً تاریخ دیگری انتخاب کنید.'
                    )

        return cleaned_data


class ManagerDecisionForm(forms.ModelForm):
    """
    فرم تصمیم‌گیری مدیر پیرامون تایید یا رد قرارداد اجاره همراه با یادداشت مدیریتی.
    """
    STATUS_CHOICES = (
        ('APPROVED', 'تأیید درخواست و فعال‌سازی قرارداد'),
        ('REJECTED', 'رد درخواست اجاره'),
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='تصمیم مدیر',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RentalContract
        fields = ['status', 'manager_note']
        widgets = {
            'manager_note': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'علت تایید یا رد، دستورالعمل‌های تحویل، یا توضیحات برای مشتری...'
                }
            ),
        }
        labels = {
            'status': 'وضعیت جدید',
            'manager_note': 'یادداشت و توضیحات مدیر',
        }
