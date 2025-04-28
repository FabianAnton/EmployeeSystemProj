import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Attendance
from employees.models import Employee


# ========================
# Employee Attendance Views
# ========================

def clock_in(request, employee_id):
    """Handles Clock In action."""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=now().date()
    )

    if attendance.clock_in_time:
        return redirect("employee_home", employee_id=employee_id)

    attendance.clock_in_time = now()
    attendance.save()
    return redirect("employee_home", employee_id=employee_id)


def start_break(request, employee_id):
    """Handles Start Break action."""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    if attendance and attendance.clock_in_time and not attendance.break_start_time:
        attendance.break_start_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)


def end_break(request, employee_id):
    """Handles End Break action."""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    if attendance and attendance.break_start_time and not attendance.break_end_time:
        attendance.break_end_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)


def clock_out(request, employee_id):
    """Handles Clock Out action."""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    if attendance and attendance.clock_in_time and not attendance.clock_out_time:
        attendance.clock_out_time = now()
        attendance.save()

    return redirect("employee_home", employee_id=employee_id)


# ========================
# Employee Home and Manager Views
# ========================

def employee_home(request, employee_id):
    """Shows employee home page with Clock In/Clock Out options."""
    employee = Employee.objects.get(employee_id=employee_id)
    attendance = Attendance.objects.filter(employee=employee, date=now().date()).first()

    context = {
        "employee": employee,
        "attendance": attendance,
    }
    return render(request, "employee_home.html", context)


def manager_dashboard(request):
    """Displays all employees and their attendance records for the manager."""
    employees = Employee.objects.prefetch_related('attendance_set').all()
    return render(request, 'manager_dashboard.html', {'employees': employees})


def employee_attendance_records(request, employee_id):
    """Displays attendance records for a specific employee."""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    records = Attendance.objects.filter(employee=employee).order_by('-date')

    return render(request, 'employee_attendance_records.html', {
        'employee': employee,
        'records': records,
    })


# ========================
# Export Attendance Data
# ========================

def export_attendance_csv(request, employee_id=None):
    """Exports attendance records to a CSV file (all employees or a single one)."""
    response = HttpResponse(content_type='text/csv')
    filename = f"attendance_{employee_id or 'all'}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Name', 'Date', 'Clock In', 'Break Start', 'Break End', 'Clock Out', 'Total Hours'])

    if employee_id:
        records = Attendance.objects.filter(employee__employee_id=employee_id)
    else:
        records = Attendance.objects.all()

    for record in records:
        writer.writerow([
            record.employee.employee_id,
            record.employee.name,
            record.date,
            record.clock_in_time.strftime("%Y-%m-%d %H:%M") if record.clock_in_time else '',
            record.break_start_time.strftime("%Y-%m-%d %H:%M") if record.break_start_time else '',
            record.break_end_time.strftime("%Y-%m-%d %H:%M") if record.break_end_time else '',
            record.clock_out_time.strftime("%Y-%m-%d %H:%M") if record.clock_out_time else '',
            record.total_hours()
        ])

    return response
