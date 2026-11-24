import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from rentals.models import RentalContract

logger = logging.getLogger('accounts')
security_logger = logging.getLogger('security_audit')


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def register_view(request):
    """
    نمای ثبت‌نام کاربر جدید (مشتری یا مدیر سامانه).
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            client_ip = _get_client_ip(request)
            logger.info("ثبت‌نام کاربر جدید: '%s' با نقش %s از IP=%s", user.username, user.role, client_ip)
            security_logger.info("USER_REGISTERED | username=%s | role=%s | ip=%s", user.username, user.role, client_ip)
            messages.success(request, f'خوش آمدید {user.get_full_name() or user.username}! حساب کاربری شما با موفقیت ایجاد شد.')
            return redirect('core:home')
        else:
            logger.warning("تلاش ناموفق برای ثبت‌نام کاربر از IP=%s: %s", _get_client_ip(request), form.errors.as_json())
            messages.error(request, 'لطفاً خطاهای موجود در فرم را تصحیح فرمایید.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    نمای ورود به سامانه با پشتیبانی از بازگشت به صفحه قبلی (next).
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        client_ip = _get_client_ip(request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info("ورود موفق کاربر '%s' (نقش: %s) از IP=%s", user.username, user.role, client_ip)
            security_logger.info("LOGIN_SUCCESS | username=%s | role=%s | ip=%s", user.username, user.role, client_ip)
            messages.success(request, f'{user.get_full_name() or user.username} گرامی، با موفقیت وارد شدید.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:home')
        else:
            attempted_username = request.POST.get('username', '').strip() or 'anonymous'
            logger.warning("تلاش ناموفق ورود برای نام کاربری '%s' از IP=%s", attempted_username, client_ip)
            security_logger.warning("LOGIN_FAILED | username=%s | ip=%s", attempted_username, client_ip)
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    نمای خروج کاربر از سامانه.
    """
    if request.user.is_authenticated:
        username = request.user.username
        client_ip = _get_client_ip(request)
        logout(request)
        logger.info("خروج کاربر '%s' از سامانه (IP=%s)", username, client_ip)
        security_logger.info("LOGOUT | username=%s | ip=%s", username, client_ip)
        messages.info(request, 'با موفقیت از حساب کاربری خود خارج شدید.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """
    نمای پروفایل کاربری و ویرایش مشخصات فردی.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            logger.info("به‌روزرسانی پروفایل توسط کاربر '%s' (تغییرات: %s)", request.user.username, form.changed_data)
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت به‌روزرسانی شد.')
            return redirect('accounts:profile')
        else:
            logger.warning("خطا در ویرایش پروفایل کاربر '%s': %s", request.user.username, form.errors.as_json())
            messages.error(request, 'لطفاً خطاهای فرم پروفایل را برطرف نمایید.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    # خلاصه آخرین رزروهای کاربر
    recent_rentals = (
        RentalContract.objects.for_customer(request.user)
        .select_related('car', 'car__brand')
        .order_by('-created_at')[:5]
    )

    context = {
        'form': form,
        'recent_rentals': recent_rentals,
    }
    return render(request, 'accounts/profile.html', context)
