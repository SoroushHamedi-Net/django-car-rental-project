from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from fleet.models import Car
from .models import RentalContract
from .forms import RentalRequestForm, ManagerDecisionForm


@login_required
def create_rental_request_view(request, car_id):
    """
    نمای ثبت درخواست اجاره توسط مشتری برای یک خودرو مشخص.
    """
    car = get_object_or_404(Car, pk=car_id)

    if car.status != 'AVAILABLE':
        messages.error(request, 'متأسفانه این خودرو در حال حاضر قابل اجاره نمی‌باشد.')
        return redirect('fleet:car_detail', pk=car.pk)

    if request.method == 'POST':
        form = RentalRequestForm(request.POST, car=car)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.car = car
            contract.customer = request.user
            contract.status = 'PENDING'
            contract.save()
            messages.success(
                request,
                f'درخواست اجاره شما برای {car.brand.name} {car.model_name} با کد رهگیری {contract.contract_code} با موفقیت ثبت شد و در انتظار تایید مدیر است.'
            )
            return redirect('rentals:my_rentals')
        else:
            messages.error(request, 'لطفاً خطاهای موجود در فرم درخواست اجاره را برطرف فرمایید.')
            similar_cars = Car.objects.filter(brand=car.brand).exclude(pk=car.pk)[:3]
            return render(request, 'fleet/car_detail.html', {
                'car': car,
                'rental_form': form,
                'similar_cars': similar_cars,
            })

    return redirect('fleet:car_detail', pk=car.pk)


@login_required
def my_rentals_view(request):
    """
    نمای مشاهده تاریخچه و قراردادهای جاری مشتری.
    """
    contracts = RentalContract.objects.filter(customer=request.user).select_related('car', 'car__brand').order_by('-created_at')

    stats = {
        'total': contracts.count(),
        'pending': contracts.filter(status='PENDING').count(),
        'approved': contracts.filter(status='APPROVED').count(),
        'completed': contracts.filter(status='COMPLETED').count(),
    }

    context = {
        'contracts': contracts,
        'stats': stats,
    }
    return render(request, 'rentals/my_rentals.html', context)


@login_required
def cancel_rental_request_view(request, pk):
    """
    امکان لغو درخواست معلق یا آینده توسط مشتری.
    """
    contract = get_object_or_404(RentalContract, pk=pk, customer=request.user)

    if contract.status in ['PENDING', 'APPROVED']:
        contract.status = 'CANCELLED'
        contract.save()
        messages.success(request, f'قرارداد {contract.contract_code} با موفقیت توسط شما لغو گردید.')
    else:
        messages.warning(request, 'امکان لغو این قرارداد در وضعیت فعلی وجود ندارد.')

    return redirect('rentals:my_rentals')


@login_required
def manager_contracts_list_view(request):
    """
    پنل مدیریت کلیه قراردادها و درخواست‌های رزرواسیون برای مدیر سامانه.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز: این صفحه مخصوص مدیران سامانه است.')
        return redirect('core:home')

    status_filter = request.GET.get('status')
    contracts = RentalContract.objects.select_related('customer', 'car', 'car__brand', 'reviewed_by').all()

    if status_filter and status_filter in dict(RentalContract.STATUS_CHOICES):
        contracts = contracts.filter(status=status_filter)

    stats = {
        'total': RentalContract.objects.count(),
        'pending': RentalContract.objects.filter(status='PENDING').count(),
        'approved': RentalContract.objects.filter(status='APPROVED').count(),
        'rejected': RentalContract.objects.filter(status='REJECTED').count(),
        'cancelled': RentalContract.objects.filter(status='CANCELLED').count(),
        'completed': RentalContract.objects.filter(status='COMPLETED').count(),
    }

    context = {
        'contracts': contracts,
        'stats': stats,
        'current_filter': status_filter or 'ALL',
    }
    return render(request, 'rentals/manager_contracts_list.html', context)


@login_required
def manager_contract_review_view(request, pk):
    """
    نمای بررسی و اعلام تصمیم مدیر (تأیید یا رد قرارداد) به صورت یک تراکنش امن دیتابیسی.
    """
    if not request.user.is_manager:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('core:home')

    contract = get_object_or_404(
        RentalContract.objects.select_related('customer', 'car', 'car__brand'),
        pk=pk
    )

    if request.method == 'POST':
        form = ManagerDecisionForm(request.POST, instance=contract)
        if form.is_valid():
            with transaction.atomic():
                updated_contract = form.save(commit=False)
                updated_contract.reviewed_by = request.user
                updated_contract.save()

                # در صورتی که قرارداد تایید شد، خودرو می‌تواند در وضعیت اجاره شده علامت‌گذاری شود
                if updated_contract.status == 'APPROVED':
                    car = updated_contract.car
                    car.status = 'RENTED'
                    car.save()

            messages.success(
                request,
                f'قرارداد {contract.contract_code} با موفقیت بررسی و به وضعیت «{updated_contract.get_status_display()}» تغییر یافت.'
            )
            return redirect('rentals:manager_contracts_list')
        else:
            messages.error(request, 'لطفاً خطاهای فرم بررسی را اصلاح فرمایید.')
    else:
        form = ManagerDecisionForm(instance=contract)

    return render(request, 'rentals/manager_contract_review.html', {
        'contract': contract,
        'form': form,
    })
