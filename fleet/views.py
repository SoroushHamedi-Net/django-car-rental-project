from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Car, CarBrand
from .forms import CarForm, CarStatusUpdateForm, CarSearchFilterForm, BrandForm
from .utils import get_recently_viewed_cars
from rentals.forms import RentalRequestForm


FILTER_PARAM_KEYS = ('brand', 'model_query', 'max_price', 'capacity', 'start_date', 'end_date')
VIEW_MODE_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 روز


def car_list_view(request):
    """
    نمای لیست ناوگان خودروها به همراه فیلتر پیشرفته، ذخیره جستجو در سشن،
    حالت نمایش شبکه‌ای/لیستی در کوکی و بخش خودروهای اخیراً مشاهده‌شده.
    """
    if request.GET.get('clear_filters') == '1':
        request.session.pop('last_search_filters', None)
        return redirect('fleet:car_list')

    cars = Car.objects.select_related('brand').all()

    has_filter_params = any(key in request.GET for key in FILTER_PARAM_KEYS)
    saved_filters = request.session.get('last_search_filters')

    if has_filter_params:
        form = CarSearchFilterForm(request.GET)
    elif saved_filters and any(saved_filters.values()):
        form = CarSearchFilterForm(saved_filters)
    else:
        form = CarSearchFilterForm()

    has_active_filters = False
    if form.is_bound and form.is_valid():
        brand = form.cleaned_data.get('brand')
        model_query = form.cleaned_data.get('model_query')
        max_price = form.cleaned_data.get('max_price')
        capacity = form.cleaned_data.get('capacity')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if brand:
            cars = cars.filter(brand=brand)
        if model_query:
            cars = cars.filter(model_name__icontains=model_query)
        if max_price is not None:
            cars = cars.by_price_range(max_price=max_price)
        if capacity is not None:
            cars = cars.filter(capacity__gte=capacity)
        if start_date and end_date:
            # حذف خودروهایی که در این بازه قرارداد معلق یا تایید شده دارند با استفاده از منیجر سفارشی
            cars = cars.available_for_dates(start_date, end_date)

        serialized_filters = {
            'brand': str(brand.pk) if brand else '',
            'model_query': model_query or '',
            'max_price': str(max_price) if max_price is not None else '',
            'capacity': str(capacity) if capacity is not None else '',
            'start_date': start_date.isoformat() if start_date else '',
            'end_date': end_date.isoformat() if end_date else '',
        }
        has_active_filters = any(serialized_filters.values())
        if has_filter_params:
            request.session['last_search_filters'] = serialized_filters

    # تعیین حالت نمایش (شبکه‌ای یا لیستی) از پارامتر URL یا کوکی مرورگر
    requested_view = request.GET.get('view')
    if requested_view in ('grid', 'list'):
        view_mode = requested_view
    else:
        cookie_view = request.COOKIES.get('car_view_mode', 'grid')
        view_mode = cookie_view if cookie_view in ('grid', 'list') else 'grid'

    recently_viewed_cars = get_recently_viewed_cars(request)

    context = {
        'cars': cars,
        'form': form,
        'total_results': cars.count(),
        'view_mode': view_mode,
        'has_active_filters': has_active_filters,
        'recently_viewed_cars': recently_viewed_cars,
    }
    response = render(request, 'fleet/car_list.html', context)

    if requested_view in ('grid', 'list') or 'car_view_mode' not in request.COOKIES:
        response.set_cookie(
            'car_view_mode',
            view_mode,
            max_age=VIEW_MODE_COOKIE_MAX_AGE,
            samesite='Lax',
        )

    return response


def car_detail_view(request, pk):
    """
    نمای جزییات مشخصات کامل خودرو، ثبت در لیست اخیراً مشاهده‌شده‌های سشن،
    پیش‌پرکردن تاریخ‌های جستجوی قبلی از سشن و نمایش فرم رزرو.
    """
    car = get_object_or_404(Car.objects.select_related('brand'), pk=pk)

    # ذخیره ۵ خودروی اخیر مشاهده‌شده در سشن
    recent_ids = list(request.session.get('recently_viewed_cars', []))
    if car.pk in recent_ids:
        recent_ids.remove(car.pk)
    recent_ids.insert(0, car.pk)
    request.session['recently_viewed_cars'] = recent_ids[:5]
    request.session.modified = True

    # پیش‌پرکردن خودکار تاریخ‌های شروع و پایان از آخرین جستجوی ذخیره‌شده در سشن
    last_filters = request.session.get('last_search_filters', {})
    initial_dates = {}
    for field_name in ('start_date', 'end_date'):
        raw_val = last_filters.get(field_name)
        if raw_val:
            try:
                initial_dates[field_name] = date.fromisoformat(raw_val)
            except (TypeError, ValueError):
                pass

    rental_form = RentalRequestForm(car=car, initial=initial_dates)
    similar_cars = Car.objects.filter(brand=car.brand).exclude(pk=car.pk)[:3]

    context = {
        'car': car,
        'rental_form': rental_form,
        'similar_cars': similar_cars,
        'prefilled_dates': bool(initial_dates),
    }
    return render(request, 'fleet/car_detail.html', context)


@login_required
def manager_car_list_view(request):
    """
    پنل مدیریت ناوگان برای مدیر سامانه.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز: این بخش مخصوص مدیران سامانه است.')
        return redirect('fleet:car_list')

    cars = Car.objects.select_related('brand').all()
    stats = {
        'total': cars.count(),
        'available': Car.objects.available().count(),
        'maintenance': Car.objects.in_maintenance().count(),
        'rented': Car.objects.rented().count(),
    }

    context = {
        'cars': cars,
        'stats': stats,
    }
    return render(request, 'fleet/manager_car_list.html', context)


@login_required
def car_create_view(request):
    """
    نمای افزودن خودرو جدید به ناوگان توسط مدیر سامانه.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز: تنها مدیران مجاز به تعریف خودرو هستند.')
        return redirect('fleet:car_list')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.created_by = request.user
            car.save()
            messages.success(request, f'خودرو {car.brand.name} {car.model_name} با موفقیت به ناوگان افزوده شد.')
            return redirect('fleet:manager_car_list')
        else:
            messages.error(request, 'لطفاً خطاهای فرم ثبت خودرو را برطرف کنید.')
    else:
        form = CarForm()

    return render(request, 'fleet/car_form.html', {'form': form, 'title': 'افزودن خودرو جدید به ناوگان'})


@login_required
def car_update_view(request, pk):
    """
    نمای ویرایش اطلاعات خودرو توسط مدیر سامانه.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز: تنها مدیران مجاز به ویرایش خودرو هستند.')
        return redirect('fleet:car_list')

    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'اطلاعات خودرو {car.brand.name} {car.model_name} با موفقیت به‌روزرسانی شد.')
            return redirect('fleet:manager_car_list')
        else:
            messages.error(request, 'لطفاً خطاهای فرم ویرایش را برطرف کنید.')
    else:
        form = CarForm(instance=car)

    return render(request, 'fleet/car_form.html', {'form': form, 'title': f'ویرایش خودرو {car.model_name}', 'car': car})


@login_required
def car_status_change_view(request, pk):
    """
    تغییر سریع وضعیت خودرو توسط مدیر.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('fleet:car_list')

    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Car.STATUS_CHOICES):
            car.status = new_status
            car.save()
            messages.success(request, f'وضعیت خودرو به «{car.get_status_display()}» تغییر یافت.')
        else:
            messages.error(request, 'وضعیت نامعتبر ارسال شده است.')

    return redirect('fleet:manager_car_list')


@login_required
def brand_create_view(request):
    """
    نمای افزودن برند جدید خودرو توسط مدیر.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('fleet:car_list')

    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'برند {brand.name} با موفقیت در سیستم ثبت گردید.')
            return redirect('fleet:manager_car_list')
        else:
            messages.error(request, 'خطایی در ثبت برند رخ داده است.')
    else:
        form = BrandForm()

    return render(request, 'fleet/brand_form.html', {'form': form})
