from django.urls import path
from . import views

app_name = 'lock'

urlpatterns = [
    path('cards/', views.get_cards, name='cards'),
    path('locks/', views.get_locks, name='locks'),
    path('search/', views.search, name='search'),

    path('create_lock/', views.create_lock, name='create_lock'),
    path('create_card/', views.create_card, name='create_card'),
    path('assign_card_to_lock/<str:lock_name>/', views.assign_card_to_lock, name='assign_card_to_lock'),

    path('remove_lock/<str:lock_name>', views.remove_lock, name='remove_lock'),
    path('remove_card/<str:card_number>', views.remove_card, name='remove_card'),
    path('remove_assigned_card/<str:lock_name>', views.remove_assigned_card, name='remove_assigned_card'),
]
