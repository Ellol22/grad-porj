from django.urls import path
from . import views

urlpatterns = [
    path('generate_qr/live/<int:course_id>/', views.qr_generation_page, name='qr_generation_page'),
    path('generate_qr/ajax/<int:course_id>/', views.generate_qr_code_ajax, name='generate_qr_ajax'),
    path('student_page/', views.student_attendance_page, name='student_attendance'),
    path('verify_qr/', views.verify_qr_code, name='verify_qr'),
    path('verify_location/', views.verify_location, name='verify_location'),
]