from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Attendance
from employees.models import Employee

def clock_in(request, employee_id):
    """Handles Clock In action"""
    employee = Employee.objects.get(employee_id=employee_id)

    # Get or create today's attendance entry
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=now().date()
    )

    # If already clocked in, do nothing
    if attendance.clock_in_time:
        return redirect("employee_home", employee_id=employee_id)

    # Update Clock In time
    attendance.clock_in_time = now()
    attendance.save()
    return redirect("employee_home", employee_id=employee_id)

def start_break(request, employee_id):
    """Handles Start Break action"""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    # Ensure employee is clocked in before starting a break
    if attendance and attendance.clock_in_time and not attendance.break_start_time:
        attendance.break_start_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)

def end_break(request, employee_id):
    """Handles End Break action"""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    # Ensure break has started before ending it
    if attendance and attendance.break_start_time and not attendance.break_end_time:
        attendance.break_end_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)

def clock_out(request, employee_id):
    """Handles Clock Out action"""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    # Allow Clock Out anytime after Clock In
    if attendance and attendance.clock_in_time and not attendance.clock_out_time:
        attendance.clock_out_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)


def employee_home(request, employee_id):
    """Show employee home page with Clock In/Clock Out options"""
    employee = Employee.objects.get(employee_id=employee_id)

    # Get today's attendance record (if exists)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    context = {
        "employee": employee,
        "attendance": attendance,
    }
    return render(request, "employee_home.html", context)

def manager_dashboard(request):
    """Displays all employees and their attendance records for the manager"""
    employees = Employee.objects.prefetch_related('attendance_set').all()
    return render(request, 'manager_dashboard.html', {'employees': employees})

def employee_attendance_records(request, employee_id):
    """Displays attendance records for a specific employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    records = Attendance.objects.filter(employee=employee).order_by('-date')

    return render(request, 'employee_attendance_records.html', {
        'employee': employee,
        'records': records
    })