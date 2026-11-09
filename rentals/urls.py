from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('request/<int:car_id>/', views.create_rental_request_view, name='create_request'),
    path('my-rentals/', views.my_rentals_view, name='my_rentals'),
    path('cancel/<int:pk>/', views.cancel_rental_request_view, name='cancel_request'),
    path('manager/', views.manager_contracts_list_view, name='manager_contracts_list'),
    path('manager/<int:pk>/review/', views.manager_contract_review_view, name='manager_contract_review'),
]
