from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('update_employee/<str:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<str:employee_id>/', views.delete_employee, name='delete_employee'),
    path('employee/<str:employee_id>/', views.employee_home, name='employee_home'),
    path('logout/', views.logout_view, name='logout'),
]
