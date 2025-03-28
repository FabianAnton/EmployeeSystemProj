from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime
from employees.models import Employee, Department
from .models import Attendance
from django.urls import reverse

class AttendanceHoursTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.emp = Employee.objects.create(
            employee_id="123456",
            name="Tester",
            department=self.department
        )
        self.attendance = Attendance.objects.create(
            employee=self.emp,
            date=make_aware(datetime(2025, 3, 27)).date(),
            clock_in_time=make_aware(datetime(2025, 3, 27, 9, 0)),
            break_start_time=make_aware(datetime(2025, 3, 27, 13, 0)),
            break_end_time=make_aware(datetime(2025, 3, 27, 14, 0)),
            clock_out_time=make_aware(datetime(2025, 3, 27, 18, 0)),
        )

    def test_total_hours(self):
        self.assertEqual(self.attendance.total_hours(), "08:00")


class AttendanceViewTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.emp = Employee.objects.create(
            employee_id="111111",
            name="Fabian",
            department=self.department
        )

    def test_attendance_page_renders(self):
        url = reverse('employee_attendance_records', args=[self.emp.employee_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attendance Records for Fabian")
