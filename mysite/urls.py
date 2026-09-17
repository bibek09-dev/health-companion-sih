from django.contrib import admin
from django.urls import path
from core_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page),
    path('doc-login/', views.doctor_login_view),   # 👈 Added
    path('doc-logout/', views.doctor_logout_view), # 👈 Added
    path('add-doctor/', views.add_doctor_view),
    path('add-medication/', views.add_medication_view),
]