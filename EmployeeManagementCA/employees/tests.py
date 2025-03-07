from django.test import TestCase, Client
from django.urls import reverse
from .models import Employee

class EmployeeModelTest(TestCase):
    def setUp(self):
        """Set up a test employee"""
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False
        )

    def test_employee_creation(self):
        """Test if the employee Fabian is created correctly"""
        self.assertEqual(self.employee.employee_id, "111111")
        self.assertEqual(self.employee.name, "Fabian")
        self.assertFalse(self.employee.is_manager)

class AuthenticationTest(TestCase):
    def setUp(self):
        """Set up test manager and employee"""
        self.client = Client()
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True
        )
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False
        )

    def test_login_manager(self):
        """Test if manager Harry can log in"""
        response = self.client.post(reverse('login'), {
            'employee_id': '123456',
            'passcode': '123456'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('manager_dashboard'))

    def test_login_employee(self):
        """Test if employee Fabian can log in"""
        response = self.client.post(reverse('login'), {
            'employee_id': '111111',
            'passcode': '111111'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('employee_home', args=['111111']))

    def test_login_invalid_credentials(self):
        """Test login with incorrect credentials"""
        response = self.client.post(reverse('login'), {
            'employee_id': '999999',
            'passcode': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, "Invalid credentials")

    def test_logout(self):
        """Test logout functionality"""
        self.client.force_login(self.manager)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertRedirects(response, reverse('login'))

class ManagerDashboardTest(TestCase):
    def setUp(self):
        """Set up test manager"""
        self.client = Client()
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True
        )

    def test_manager_dashboard_access(self):
        """Test if manager Harry can access the dashboard"""
        self.client.force_login(self.manager)
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manager Dashboard")

class EmployeeHomeTest(TestCase):
    def setUp(self):
        """Set up test employee Fabian"""
        self.client = Client()
        self.employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False
        )

    def test_employee_home_access(self):
        """Test if employee Fabian can access home page"""
        self.client.force_login(self.employee)
        response = self.client.get(reverse('employee_home', args=['111111']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Fabian!")

class EmployeeManagementTest(TestCase):
    def setUp(self):
        """Set up test manager Harry"""
        self.client = Client()
        self.manager = Employee.objects.create_employee(
            employee_id="123456",
            name="Harry",
            passcode="123456",
            is_manager=True
        )
        self.client.force_login(self.manager)

    def test_add_employee(self):
        """Test adding a new employee"""
        response = self.client.post(reverse('add_employee'), {
            'employee_id': '222222',
            'name': 'New Employee',
            'passcode': '222222',
            'is_manager': False
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to manager dashboard
        self.assertTrue(Employee.objects.filter(employee_id='222222').exists())

    def test_update_employee(self):
        """Test updating an employee"""
        employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False
        )
        response = self.client.post(reverse('update_employee', args=[employee.employee_id]), {
            'name': 'Fabian Updated',
            'passcode': '654321',
            'is_manager': True
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        updated_employee = Employee.objects.get(employee_id="111111")
        self.assertEqual(updated_employee.name, "Fabian Updated")
        self.assertTrue(updated_employee.is_manager)

    def test_delete_employee(self):
        """Test deleting an employee"""
        employee = Employee.objects.create_employee(
            employee_id="111111",
            name="Fabian",
            passcode="111111",
            is_manager=False
        )
        response = self.client.get(reverse('delete_employee', args=[employee.employee_id]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertFalse(Employee.objects.filter(employee_id="111111").exists())

