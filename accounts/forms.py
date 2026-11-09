from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    """
    فرم ثبت‌نام کاربر جدید با پشتیبانی از نقش کاربری، شماره تماس و کد ملی.
    """
    email = forms.EmailField(
        required=True,
        label='آدرس ایمیل',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='نام',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خود را وارد کنید'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی خود را وارد کنید'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label='شماره همراه',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹', 'dir': 'ltr'})
    )
    national_code = forms.CharField(
        max_length=10,
        required=False,
        label='کد ملی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد ملی ۱۰ رقمی (اختیاری)', 'dir': 'ltr'})
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        initial='CUSTOMER',
        label='نقش کاربری',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'national_code',
            'role',
            'password_1',
            'password_2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'نام کاربری انگلیسی', 'dir': 'ltr'})
        self.fields['username'].label = 'نام کاربری'
        self.fields['password_1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'رمز عبور امن', 'dir': 'ltr'})
        self.fields['password_1'].label = 'رمز عبور'
        self.fields['password_2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تکرار رمز عبور', 'dir': 'ltr'})
        self.fields['password_2'].label = 'تکرار رمز عبور'

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = phone.strip()
            if not phone.isdigit() or len(phone) < 10 or len(phone) > 15:
                raise ValidationError('شماره تماس معتبر نیست (باید عددی بین ۱۰ تا ۱۵ رقم باشد).')
            if CustomUser.objects.filter(phone_number=phone).exists():
                raise ValidationError('این شماره تماس قبلاً در سامانه ثبت شده است.')
        return phone

    def clean_national_code(self):
        code = self.cleaned_data.get('national_code')
        if code:
            code = code.strip()
            if not code.isdigit() or len(code) != 10:
                raise ValidationError('کد ملی باید دقیقاً ۱۰ رقم عددی باشد.')
        return code


class UserLoginForm(AuthenticationForm):
    """
    فرم ورود کاربران با استایل بوت‌استرپ و پیام‌های راهنما.
    """
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری', 'dir': 'ltr', 'autofocus': True})
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور', 'dir': 'ltr'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    فرم ویرایش اطلاعات کاربری و پروفایل.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'national_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'آدرس ایمیل',
            'phone_number': 'شماره همراه',
            'national_code': 'کد ملی',
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = phone.strip()
            exists = CustomUser.objects.filter(phone_number=phone).exclude(pk=self.instance.pk).exists()
            if exists:
                raise ValidationError('این شماره همراه توسط کاربر دیگری ثبت شده است.')
        return phone
