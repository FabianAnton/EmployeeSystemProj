from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from .models import Employee, Department

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
            'employee_id': '222222',
            'name': 'New Employee',
            'passcode': '222222',
            'department': self.department.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employee.objects.filter(employee_id='222222').exists())

    def test_update_employee(self):
        employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False,
            department=self.department
        )
        response = self.client.post(reverse('update_employee', args=[employee.employee_id]), {
            'name': 'Fabian Updated',
            'passcode': '654321',
            'is_manager': True,
            'department': self.department.id
        })
        self.assertEqual(response.status_code, 302)
        updated_employee = Employee.objects.get(employee_id="111111")
        self.assertEqual(updated_employee.name, "Fabian Updated")
        self.assertTrue(updated_employee.is_manager)

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
