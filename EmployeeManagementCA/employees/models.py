from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Department(models.Model):
    Department_name = models.CharField(max_length=100, default='General')
    
    def __str__(self):
        return self.Department_name


class EmployeeManager(BaseUserManager):
    def create_employee(self, employee_id, name, passcode, is_manager=False, department=None):
        employee = self.model(
            employee_id=employee_id,
            name=name,
            passcode=passcode,
            is_manager=is_manager,
            department=department  
        )
        employee.save(using=self._db)
        return employee

    def create_manager(self, employee_id, name, passcode, department=None):
        return self.create_employee(
            employee_id, name, passcode, is_manager=True, department=department
        )


class Employee(AbstractBaseUser):
    employee_id = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=100)
    passcode = models.CharField(max_length=6)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='employees',
        null=False,
        default=""
    )
    is_manager = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    archive_date = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,default='profile_pictures/default.jpg')

    objects = EmployeeManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.employee.name} ({self.start_date} - {self.end_date})"