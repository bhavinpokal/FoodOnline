from django.urls import path
from accounts import views


urlpatterns = [
    # Registration and activation
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Login-Logout
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Dashboard
    path('custDashboard/', views.custDashboard, name='custDashboard'),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard'),
    path('myAccount/', views.myAccount, name='myAccount'),

    # Password reset
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/',
         views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
