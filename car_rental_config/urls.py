"""
URL configuration for car_rental_config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# تنظیمات فارسی پنل مدیریت جنگو
admin.site.site_header = 'سامانه مدیریت اجاره خودرو'
admin.site.site_title = 'پنل مدیریت اجاره خودرو'
admin.site.index_title = 'مدیریت و کنترل ناوگان و قراردادها'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('fleet/', include('fleet.urls')),
    path('rentals/', include('rentals.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
