from django import forms
from .models import Car, CarBrand


class CarForm(forms.ModelForm):
    """
    فرم ثبت و ویرایش خودرو برای مدیر سامانه / ناوگان.
    """
    class Meta:
        model = Car
        fields = [
            'brand',
            'model_name',
            'year',
            'daily_price',
            'capacity',
            'features',
            'status',
            'pickup_address',
            'latitude',
            'longitude',
            'image',
        ]
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: سوناتا YF، کمری، ۲۰۶'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: ۱۴۰۱ یا ۲۰۲۲'}),
            'daily_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'نرخ به تومان'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 15}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'امکانات رفاهی و ایمنی خودرو'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'pickup_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'آدرس کامل دفتر یا پارکینگ تحویل'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'id': 'id_longitude'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'brand': 'برند سازنده',
            'model_name': 'مدل خودرو',
            'year': 'سال ساخت',
            'daily_price': 'قیمت اجاره روزانه (تومان)',
            'capacity': 'ظرفیت سرنشین (نفر)',
            'features': 'امکانات و آپشن‌ها',
            'status': 'وضعیت خودرو',
            'pickup_address': 'آدرس محل تحویل',
            'latitude': 'عرض جغرافیایی (Latitude)',
            'longitude': 'طول جغرافیایی (Longitude)',
            'image': 'تصویر شاخص خودرو',
        }


class CarStatusUpdateForm(forms.ModelForm):
    """
    فرم سریع تغییر وضعیت عملیاتی خودرو توسط مدیر.
    """
    class Meta:
        model = Car
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'وضعیت جدید خودرو',
        }


class CarSearchFilterForm(forms.Form):
    """
    فرم جستجو و فیلتر پیشرفته خودروها برای مشتریان و کاربران عمومی.
    """
    brand = forms.ModelChoiceField(
        queryset=CarBrand.objects.all(),
        required=False,
        empty_label='همه برندها',
        label='برند',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    model_query = forms.CharField(
        max_length=100,
        required=False,
        label='مدل یا نام خودرو',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'جستجو در نام و مدل...'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        label='حداکثر قیمت روزانه (تومان)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: ۵,۰۰۰,۰۰۰'})
    )
    capacity = forms.IntegerField(
        required=False,
        min_value=1,
        label='حداقل ظرفیت سرنشین',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'تعداد نفرات'})
    )
    start_date = forms.DateField(
        required=False,
        label='تاریخ تحویل (شروع)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label='تاریخ عودت (پایان)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class BrandForm(forms.ModelForm):
    """
    فرم افزودن برند جدید خودرو توسط مدیر.
    """
    class Meta:
        model = CarBrand
        fields = ['name', 'country', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: بنز، کیا، هیوندای'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: آلمان، کره جنوبی'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'نام برند',
            'country': 'کشور سازنده',
            'logo': 'لوگو یا تصویر برند',
        }
