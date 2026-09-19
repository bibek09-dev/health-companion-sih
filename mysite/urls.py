from django.contrib import admin
from django.urls import path
from core_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page),
    path('login/', views.system_login_view),
    path('logout/', views.system_logout_view),
    path('add-patient/', views.add_patient_view),
    path('add-doctor/', views.add_doctor_view),
    path('add-medication/', views.add_medication_view),
]