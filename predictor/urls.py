from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('user-login/', views.user_login, name='user_login'),
    path('user-signup/', views.user_signup, name='user_signup'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-login/', views.admin_login, name='admin_login'),


    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
   
    path('admin-history/', views.admin_history, name='admin_history'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    path('download-report/', views.download_report, name='download_report'),
  
#prediction form and history
    path('predict/', views.prediction_form, name='predict'),
    path('prediction-history/', views.prediction_history, name='prediction_history'),

    path('resnet-metrics/', views.resnet_metrics, name='resnet_metrics'),

    path('mobilenet-metrics/', views.mobilenet_metrics, name='mobilenet_metrics'),
]