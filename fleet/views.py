from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Car, CarBrand
from .forms import CarForm, CarStatusUpdateForm, CarSearchFilterForm, BrandForm
from rentals.models import RentalContract
from rentals.forms import RentalRequestForm


def car_list_view(request):
    """
    نمای لیست ناوگان خودروها به همراه فیلتر پیشرفته بر اساس برند، مدل، سقف قیمت، ظرفیت و بازه تاریخ.
    """
    cars = Car.objects.select_related('brand').all()
    form = CarSearchFilterForm(request.GET or None)

    if form.is_valid():
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
        if max_price:
            cars = cars.filter(daily_price__lte=max_price)
        if capacity:
            cars = cars.filter(capacity__gte=capacity)
        if start_date and end_date:
            # حذف خودروهایی که در این بازه قرارداد معلق یا تایید شده دارند
            overlapping_car_ids = RentalContract.objects.filter(
                status__in=['PENDING', 'APPROVED'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values_list('car_id', flat=True)
            cars = cars.exclude(id__in=overlapping_car_ids)

    context = {
        'cars': cars,
        'form': form,
        'total_results': cars.count(),
    }
    return render(request, 'fleet/car_list.html', context)


def car_detail_view(request, pk):
    """
    نمای جزییات مشخصات کامل خودرو، امکانات، آدرس تحویل و فرم رزرو.
    """
    car = get_object_or_404(Car.objects.select_related('brand'), pk=pk)
    rental_form = RentalRequestForm(car=car)
    similar_cars = Car.objects.filter(brand=car.brand).exclude(pk=car.pk)[:3]

    context = {
        'car': car,
        'rental_form': rental_form,
        'similar_cars': similar_cars,
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
        'available': cars.filter(status='AVAILABLE').count(),
        'maintenance': cars.filter(status='MAINTENANCE').count(),
        'rented': cars.filter(status='RENTED').count(),
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
