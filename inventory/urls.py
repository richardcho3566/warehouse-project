from django.urls import path
from . import views
from .views import download_csv


urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('search-location/', views.search_by_location, name='search_by_location'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('download_csv/', download_csv, name='download_csv'),

    
]
