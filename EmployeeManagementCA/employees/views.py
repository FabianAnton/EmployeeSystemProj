from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import Employee, Department
from django.utils.timezone import now 

def login_view(request):
    if request.method == 'POST':
        employee_id = request.POST['employee_id']
        passcode = request.POST['passcode']

        try:
            employee = Employee.objects.get(employee_id=employee_id, passcode=passcode)

            if employee.is_manager:
                return redirect('manager_dashboard')
            else:
                return redirect('employee_home', employee_id=employee.employee_id)
        except Employee.DoesNotExist:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})

    return render(request, 'employees/login.html')

def manager_dashboard(request):
    employees = Employee.objects.filter(archived=False)
    return render(request, 'employees/manager_dashboard.html', {'employees': employees})

def add_employee(request):
    if request.method == 'POST':
        employee_id = request.POST['employee_id']
        name = request.POST['name']
        passcode = request.POST['passcode']
        is_manager = 'is_manager' in request.POST
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) 

        Employee.objects.create_employee(employee_id, name, passcode, is_manager, department)
        
        return redirect('manager_dashboard')

    return render(request, 'employees/add_employee.html')


# Update Employee
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.passcode = request.POST['passcode']
        employee.is_manager = 'is_manager' in request.POST  # Update manager status
        employee.save()
        return redirect('manager_dashboard')

    return render(request, 'employees/update_employee.html', {'employee': employee})

def archive_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.archived = True
    employee.archive_date = now()  # Store the archive timestamp
    employee.save()
    return redirect('manager_dashboard')

def view_archived_employees(request):
    """Displays a list of archived employees"""
    archived_employees = Employee.objects.filter(archived=True)
    return render(request, 'archived_employees.html', {'archived_employees': archived_employees})

# Delete Employee
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.delete()
    return redirect('manager_dashboard')

def employee_home(request, employee_id):
    employee = Employee.objects.get(employee_id=employee_id)
    return render(request, 'employee_home.html', {'employee': employee})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirects to the login page after logout

#department view
def department_list(request):
    departments = Department.objects.prefetch_related('employees').all()
    return render(request, 'departments.html', {'departments': departments})  
