from django.urls import path
from . import views

app_name = 'fleet'

urlpatterns = [
    path('', views.car_list_view, name='car_list'),
    path('<int:pk>/', views.car_detail_view, name='car_detail'),
    path('manager/', views.manager_car_list_view, name='manager_car_list'),
    path('manager/create/', views.car_create_view, name='car_create'),
    path('manager/<int:pk>/edit/', views.car_update_view, name='car_update'),
    path('manager/<int:pk>/status/', views.car_status_change_view, name='car_status_change'),
    path('manager/brand/create/', views.brand_create_view, name='brand_create'),
]
