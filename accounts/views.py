from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from rentals.models import RentalContract


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
            messages.success(request, f'خوش آمدید {user.get_full_name() or user.username}! حساب کاربری شما با موفقیت ایجاد شد.')
            return redirect('core:home')
        else:
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
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'{user.get_full_name() or user.username} گرامی، با موفقیت وارد شدید.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    نمای خروج کاربر از سامانه.
    """
    if request.user.is_authenticated:
        logout(request)
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
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت به‌روزرسانی شد.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'لطفاً خطاهای فرم پروفایل را برطرف نمایید.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    # خلاصه آخرین رزروهای کاربر
    recent_rentals = RentalContract.objects.filter(customer=request.user).order_by('-created_at')[:5]

    context = {
        'form': form,
        'recent_rentals': recent_rentals,
    }
    return render(request, 'accounts/profile.html', context)
