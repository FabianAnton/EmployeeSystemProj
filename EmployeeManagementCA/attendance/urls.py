from django.urls import path
from . import views

urlpatterns = [
    path('employee/<str:employee_id>/', views.employee_home, name='employee_home'),
    path('clock-in/<str:employee_id>/', views.clock_in, name='clock_in'),
    path('clock-out/<str:employee_id>/', views.clock_out, name='clock_out'),
    path('start-break/<str:employee_id>/', views.start_break, name='start_break'),
    path('end-break/<str:employee_id>/', views.end_break, name='end_break'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('records/<str:employee_id>/', views.employee_attendance_records, name='employee_attendance_records'),
    path('export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('export/<str:employee_id>/', views.export_attendance_csv, name='export_attendance_csv_employee'),
]
