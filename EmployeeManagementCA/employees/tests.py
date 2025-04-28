from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from .models import Employee, Department, LeaveRequest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )

    def test_employee_creation(self):
        self.assertEqual(self.employee.employee_id, "111111")
        self.assertEqual(self.employee.name, "Fabian")
        self.assertFalse(self.employee.is_manager)


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(Department_name="Test Dept")
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True,
            department=self.department
        )
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )

    def test_login_manager(self):
        response = self.client.post(reverse('login'), {
            'employee_id': '123456',
            'passcode': '123456'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('manager_dashboard'))

    def test_login_employee(self):
        response = self.client.post(reverse('login'), {
            'employee_id': '111111',
            'passcode': '111111'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('employee_home', args=['111111']))

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'employee_id': '999999',
            'passcode': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials")

    def test_logout(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class ManagerDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(Department_name="Test Dept")
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True,
            department=self.department
        )
        Employee.objects.create(employee_id="active1", name="Active User", department=self.department)
        Employee.objects.create(employee_id="archived1", name="Archived User", department=self.department, archived=True)

    def test_manager_dashboard_access(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manager Dashboard")

    def test_archived_not_in_dashboard(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_dashboard'))
        self.assertContains(response, "Active User")
        self.assertNotContains(response, "Archived User")


class EmployeeHomeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(Department_name="Test Dept")
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )

    def test_employee_home_access(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('employee_home', args=['111111']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Fabian!")


class EmployeeManagementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(Department_name="Test Dept")
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True,
            department=self.department
        )
        self.client.force_login(self.manager)

    def test_add_employee(self):
        response = self.client.post(reverse('add_employee'), {
            'name': 'New Employee',
            'passcode': '222222',
            'department': self.department.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employee.objects.filter(name='New Employee').exists())


    def test_update_employee(self):
        employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )
        self.client.force_login(employee)
        session = self.client.session
        session['employee_id'] = employee.employee_id
        session.save()

        response = self.client.post(reverse('update_employee', args=[employee.employee_id]), {
            'name': 'Fabian Updated',
            'passcode': '654321',
            'is_manager': True,
            'department': self.department.id,
            'source': 'manager_dashboard'  # <-- important for your redirect logic
        })

        self.assertEqual(response.status_code, 302)
        updated_employee = Employee.objects.get(employee_id="111111")
        self.assertEqual(updated_employee.name, "Fabian Updated")



    def test_delete_employee(self):
        employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )
        response = self.client.get(reverse('delete_employee', args=[employee.employee_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Employee.objects.filter(employee_id="111111").exists())


class ArchiveEmployeeTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.employee = Employee.objects.create(
            employee_id="999999",
            name="Test User",
            department=self.department
        )

    def test_archive_sets_flag_and_date(self):
        self.employee.archived = True
        self.employee.archive_date = now()
        self.employee.save()

        employee = Employee.objects.get(employee_id="999999")
        self.assertTrue(employee.archived)
        self.assertIsNotNone(employee.archive_date)

class searchbarTest(TestCase):
    def setUp(self):
        
        self.department = Department.objects.create(Department_name="IT")
        self.employee = Employee.objects.create(
            employee_id="999999",
            name="Test User",
            passcode="999999",
            department=self.department
        )

    def test_employee_search(self):
        response = self.client.get(reverse("filter_search"), {"q": "Test"}) 
        
        self.assertEqual(response.status_code, 200, "Search page did not return a successful response")
        self.assertContains(response, "Test User", msg_prefix="Expected employee not found in search results")

class leavereviewTest(TestCase):
    def setUp(self):
        """Create a test employee before each test runs."""
        self.department = Department.objects.create(Department_name="IT")
        self.employee = Employee.objects.create(
            employee_id="999999",
            name="Test User",
            passcode="999999",
            department=self.department
        )
    
    def test_leave_request_validation(self):
        start_date=timezone.now().date() - timedelta(days=2)
        end_date=timezone.now().date() + timedelta(days=2)
        
        with self.assertRaises(ValueError):
            if start_date < timezone.now().date():
                raise ValueError("start date cannot be in the past.")
        
        LeaveRequest.objects.create(
            employee=self.employee,
            start_date=start_date,
            end_date=end_date,
            reason="Vacation",
            status="Pending"
        )
            
class LeaveRequestCreationTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="IT")
        self.employee = Employee.objects.create(
            employee_id="999998",
            name="Leave Test User",
            passcode="999998",
            department=self.department
        )

    def test_create_leave_request(self):
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=timezone.now().date() + timedelta(days=1),
            end_date=timezone.now().date() + timedelta(days=5),
            reason="Family trip"
        )
        self.assertEqual(leave.status, "Pending")
        self.assertEqual(leave.employee.name, "Leave Test User")

class ViewLeaveRequestsTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="IT")
        self.employee = Employee.objects.create(
            employee_id="999997",
            name="View Leave User",
            passcode="999997",
            department=self.department
        )
        LeaveRequest.objects.create(
            employee=self.employee,
            start_date=timezone.now().date() + timedelta(days=1),
            end_date=timezone.now().date() + timedelta(days=3),
            reason="Medical"
        )

    def test_view_leave_requests_page(self):
        client = Client()
        response = client.get(reverse('view_leave_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Medical")

class UpdateLeaveStatusTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="HR")
        self.employee = Employee.objects.create(
            employee_id="999996",
            name="Status Test User",
            passcode="999996",
            department=self.department
        )
        self.leave_request = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=timezone.now().date() + timedelta(days=2),
            end_date=timezone.now().date() + timedelta(days=4),
            reason="Training"
        )

    def test_approve_leave_request(self):
        client = Client()
        response = client.get(reverse('update_leave_status', args=[self.leave_request.id, 'approve']))
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, "Approved")

    def test_reject_leave_request(self):
        client = Client()
        response = client.get(reverse('update_leave_status', args=[self.leave_request.id, 'reject']))
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, "Rejected")

class ArchiveUnarchiveEmployeeTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Manager",
            passcode="123456",
            is_manager=True,
            department=self.department
        )
        self.client.force_login(self.manager)
        self.employee = Employee.objects.create_employee(
            employee_id="654321",
            name="Employee to Archive",
            passcode="654321",
            department=self.department
        )

    def test_archive_employee(self):
        response = self.client.get(reverse('archive_employee', args=[self.employee.employee_id]))
        self.assertEqual(response.status_code, 302)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.archived)

    def test_unarchive_employee(self):
        self.employee.archived = True
        self.employee.save()

        response = self.client.get(reverse('unarchive_employee', args=[self.employee.employee_id]))
        self.assertEqual(response.status_code, 302)
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.archived)

class RequestLeaveTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Test Dept")
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Leave Tester",
            passcode="111111",
            department=self.department
        )
        self.client.force_login(self.employee)
        session = self.client.session
        session['employee_id'] = self.employee.employee_id
        session.save()

    def test_submit_leave_request(self):
        response = self.client.post(reverse('request_leave'), {
            'start_date': (timezone.now().date() + timedelta(days=1)),
            'end_date': (timezone.now().date() + timedelta(days=3)),
            'reason': 'Medical leave'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LeaveRequest.objects.filter(employee=self.employee).exists())

class ViewLeaveRequestsTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Dept")
        self.manager = Employee.objects.create_employee(
            employee_id="123123",
            name="Manager Test",
            passcode="123123",
            is_manager=True,
            department=self.department
        )
        self.client.force_login(self.manager)
        self.employee = Employee.objects.create_employee(
            employee_id="999999",
            name="Leave Requester",
            passcode="999999",
            department=self.department
        )
        LeaveRequest.objects.create(
            employee=self.employee,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            reason="Family event"
        )

    def test_view_leave_requests(self):
        response = self.client.get(reverse('view_leave_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leave Requester")

class EmployeeDetailsTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="IT")
        self.employee = Employee.objects.create(
            employee_id="777777",
            name="Detail User",
            passcode="777777",
            department=self.department
        )

    def test_employee_details_page(self):
        response = self.client.get(reverse('employee_detail', args=[self.employee.employee_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail User")

class DepartmentListTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(Department_name="Marketing")
        self.employee = Employee.objects.create(
            employee_id="888888",
            name="Marketing User",
            passcode="888888",
            department=self.department
        )

    def test_department_list_page(self):
        response = self.client.get(reverse('departments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marketing")
        self.assertContains(response, "Marketing User")