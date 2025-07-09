from django.urls import path
from . import views
from .views import download_csv, signup_view, user_list, update_grade
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('search-location/', views.search_by_location, name='search_by_location'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('download_csv/', download_csv, name='download_csv'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('users/', views.user_list, name='manage_users'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:profile_id>/update/', update_grade, name='update_grade'),\
]

