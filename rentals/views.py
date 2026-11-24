import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from fleet.models import Car
from .models import RentalContract
from .forms import RentalRequestForm, ManagerDecisionForm

logger = logging.getLogger('rentals')
security_logger = logging.getLogger('security_audit')


@login_required
def create_rental_request_view(request, car_id):
    """
    نمای ثبت درخواست اجاره توسط مشتری برای یک خودرو مشخص.
    """
    car = get_object_or_404(Car, pk=car_id)

    if car.status != 'AVAILABLE':
        logger.warning(
            "تلاش مشتری '%s' برای رزرو خودرو غیرقابل‌اجاره ID=%s (وضعیت فعلی: %s)",
            request.user.username,
            car.pk,
            car.status,
        )
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
            logger.info(
                "ثبت درخواست اجاره جدید %s توسط مشتری '%s' برای خودرو ID=%s (%s %s) از %s تا %s | مبلغ=%s",
                contract.contract_code,
                request.user.username,
                car.pk,
                car.brand.name,
                car.model_name,
                contract.start_date,
                contract.end_date,
                contract.total_price,
            )
            messages.success(
                request,
                f'درخواست اجاره شما برای {car.brand.name} {car.model_name} با کد رهگیری {contract.contract_code} با موفقیت ثبت شد و در انتظار تایید مدیر است.'
            )
            return redirect('rentals:my_rentals')
        else:
            logger.warning(
                "رد درخواست اجاره مشتری '%s' برای خودرو ID=%s (تداخل زمانی یا خطای تاریخ): %s",
                request.user.username,
                car.pk,
                form.errors.as_json(),
            )
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
    contracts = (
        RentalContract.objects.for_customer(request.user)
        .select_related('car', 'car__brand')
        .order_by('-created_at')
    )

    stats = {
        'total': contracts.count(),
        'pending': contracts.pending_requests().count(),
        'approved': contracts.active_contracts().count(),
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
        previous_status = contract.status
        contract.status = 'CANCELLED'
        contract.save()
        logger.info(
            "لغو قرارداد %s توسط مشتری '%s' (وضعیت قبلی: %s)",
            contract.contract_code,
            request.user.username,
            previous_status,
        )
        messages.success(request, f'قرارداد {contract.contract_code} با موفقیت توسط شما لغو گردید.')
    else:
        logger.warning(
            "تلاش نامعتبر مشتری '%s' برای لغو قرارداد %s در وضعیت %s",
            request.user.username,
            contract.contract_code,
            contract.status,
        )
        messages.warning(request, 'امکان لغو این قرارداد در وضعیت فعلی وجود ندارد.')

    return redirect('rentals:my_rentals')


@login_required
def manager_contracts_list_view(request):
    """
    پنل مدیریت کلیه قراردادها و درخواست‌های رزرواسیون برای مدیر سامانه.
    """
    if not request.user.is_manager:
        security_logger.warning("UNAUTHORIZED_RENTALS_ACCESS | user=%s | view=manager_contracts_list", request.user.username)
        messages.error(request, 'دسترسی غیرمجاز: این صفحه مخصوص مدیران سامانه است.')
        return redirect('core:home')

    status_filter = request.GET.get('status')
    contracts = RentalContract.objects.select_related('customer', 'car', 'car__brand', 'reviewed_by').all()

    if status_filter and status_filter in dict(RentalContract.STATUS_CHOICES):
        contracts = contracts.filter(status=status_filter)

    stats = {
        'total': RentalContract.objects.count(),
        'pending': RentalContract.objects.pending_requests().count(),
        'approved': RentalContract.objects.active_contracts().count(),
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
        security_logger.warning("UNAUTHORIZED_RENTALS_ACCESS | user=%s | view=manager_contract_review | contract_id=%s", request.user.username, pk)
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('core:home')

    contract = get_object_or_404(
        RentalContract.objects.select_related('customer', 'car', 'car__brand'),
        pk=pk
    )

    if request.method == 'POST':
        form = ManagerDecisionForm(request.POST, instance=contract)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_contract = form.save(commit=False)
                    updated_contract.reviewed_by = request.user
                    updated_contract.save()

                    # در صورتی که قرارداد تایید شد، خودرو می‌تواند در وضعیت اجاره شده علامت‌گذاری شود
                    if updated_contract.status == 'APPROVED':
                        car = updated_contract.car
                        old_car_status = car.status
                        car.status = 'RENTED'
                        car.save()
                        logger.info(
                            "تغییر خودکار وضعیت خودرو ID=%s (%s %s) پس از تایید قرارداد %s: %s -> RENTED",
                            car.pk,
                            car.brand.name,
                            car.model_name,
                            updated_contract.contract_code,
                            old_car_status,
                        )
            except Exception as exc:
                logger.error(
                    "خطای سیستمی در بررسی قرارداد %s توسط مدیر '%s': %s",
                    contract.contract_code,
                    request.user.username,
                    exc,
                    exc_info=True,
                )
                messages.error(request, 'خطای غیرمنتظره‌ای هنگام ثبت تصمیم رخ داد. لطفاً مجدداً تلاش کنید.')
                return redirect('rentals:manager_contract_review', pk=contract.pk)

            logger.info(
                "تصمیم مدیر '%s' برای قرارداد %s ثبت شد: وضعیت=%s | یادداشت='%s'",
                request.user.username,
                updated_contract.contract_code,
                updated_contract.status,
                (updated_contract.manager_note or '')[:80],
            )
            messages.success(
                request,
                f'قرارداد {contract.contract_code} با موفقیت بررسی و به وضعیت «{updated_contract.get_status_display()}» تغییر یافت.'
            )
            return redirect('rentals:manager_contracts_list')
        else:
            logger.warning(
                "خطا در فرم بررسی قرارداد %s توسط مدیر '%s': %s",
                contract.contract_code,
                request.user.username,
                form.errors.as_json(),
            )
            messages.error(request, 'لطفاً خطاهای فرم بررسی را اصلاح فرمایید.')
    else:
        form = ManagerDecisionForm(instance=contract)

    return render(request, 'rentals/manager_contract_review.html', {
        'contract': contract,
        'form': form,
    })
