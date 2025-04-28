from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.db.models import Prefetch
from django.db import models
import random

from .models import Employee, Department, LeaveRequest


# -------------------------------
# Authentication Views
# -------------------------------

def login_view(request):
    if request.method == 'POST':
        employee_id = request.POST['employee_id']
        passcode = request.POST['passcode']

        try:
            employee = Employee.objects.get(employee_id=employee_id, passcode=passcode)
            request.session['employee_id'] = employee.employee_id

            if employee.is_manager:
                return redirect('manager_dashboard')
            else:
                return redirect('employee_home', employee_id=employee.employee_id)
        except Employee.DoesNotExist:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})

    return render(request, 'employees/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------------------
# Dashboard and Employee Management Views
# -------------------------------

def manager_dashboard(request):
    employees = Employee.objects.filter(archived=False)
    return render(request, 'employees/manager_dashboard.html', {'employees': employees})


def add_employee(request):
    if request.method == 'POST':
        while True:
            employee_id = str(random.randint(100000, 999999))
            if not Employee.objects.filter(employee_id=employee_id).exists():
                break

        name = request.POST['name']
        passcode = request.POST['passcode']
        is_manager = 'is_manager' in request.POST
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id)
        profile_picture = request.FILES.get('profile_picture')

        Employee.objects.create(
            employee_id=employee_id,
            name=name,
            passcode=passcode,
            is_manager=is_manager,
            department=department,
            profile_picture=profile_picture
        )

        return redirect('manager_dashboard')

    departments = Department.objects.all()
    return render(request, 'employees/add_employee.html', {'departments': departments})


def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    current_employee_id = request.session.get('employee_id')
    logged_in_is_manager = False

    if current_employee_id:
        try:
            current_employee = Employee.objects.get(employee_id=current_employee_id)
            logged_in_is_manager = current_employee.is_manager
        except Employee.DoesNotExist:
            pass

    if not logged_in_is_manager and employee.employee_id != current_employee_id:
        return redirect('employee_home', employee_id=current_employee_id if current_employee_id else employee.employee_id)

    if request.method == 'POST':
        source = request.POST.get('source', 'manager_dashboard')
        employee.name = request.POST['name']
        employee.passcode = request.POST['passcode']

        if logged_in_is_manager:
            department_id = request.POST.get('department')
            employee.department = Department.objects.get(id=department_id)
            employee.is_manager = 'is_manager' in request.POST

        if request.FILES.get('profile_picture'):
            employee.profile_picture = request.FILES['profile_picture']

        employee.save()

        if source == 'employee_home':
            return redirect('employee_home', employee_id=employee.employee_id)
        else:
            return redirect('manager_dashboard')

    departments = Department.objects.all()
    source = request.GET.get('source', 'manager_dashboard')

    return render(request, 'employees/update_employee.html', {
        'employee': employee,
        'departments': departments,
        'source': source,
        'logged_in_is_manager': logged_in_is_manager,
    })


def archive_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.archived = True
    employee.archive_date = now()
    employee.save()
    return redirect('manager_dashboard')


def unarchive_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id, archived=True)
    employee.archived = False
    employee.archive_date = None
    employee.save()
    return redirect('manager_dashboard')


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.delete()
    return redirect('manager_dashboard')


# -------------------------------
# Employee Pages
# -------------------------------

def employee_home(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, 'employee_home.html', {'employee': employee})


def employee_details(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    source = request.GET.get('source')
    return render(request, 'employee_detail.html', {
        'employee': employee,
        'source': source,
    })


def view_archived_employees(request):
    archived_employees = Employee.objects.filter(archived=True)
    return render(request, 'archived_employees.html', {'archived_employees': archived_employees})


# -------------------------------
# Department Views
# -------------------------------

def department_list(request):
    departments = Department.objects.prefetch_related(
        Prefetch('employees', queryset=Employee.objects.filter(archived=False))
    ).all()
    return render(request, 'departments.html', {'departments': departments})


# -------------------------------
# Search Views
# -------------------------------

def filter_view(request):
    qs = Employee.objects.filter(archived=False)
    search_query = request.GET.get('search_query')

    if search_query:
        qs = qs.filter(
            models.Q(name__icontains=search_query) |
            models.Q(employee_id__icontains=search_query)
        )

    return render(request, 'search.html', {'queryset': qs})


# -------------------------------
# Leave Management Views
# -------------------------------

def request_leave(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        start = request.POST['start_date']
        end = request.POST['end_date']
        reason = request.POST['reason']

        LeaveRequest.objects.create(
            employee=employee,
            start_date=start,
            end_date=end,
            reason=reason
        )
        return redirect('employee_home', employee_id=employee.employee_id)

    return render(request, 'employees/request_leave.html', {'employee': employee})


def view_leave_requests(request):
    requests = LeaveRequest.objects.select_related('employee').order_by('-requested_at')
    return render(request, 'employees/view_leave_requests.html', {'leave_requests': requests})


def update_leave_status(request, request_id, action):
    leave = LeaveRequest.objects.get(id=request_id)
    leave.status = 'Approved' if action == 'approve' else 'Rejected'
    leave.save()
    return redirect('view_leave_requests')