from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class EmployeeManager(BaseUserManager):
    def create_employee(self, employee_id, name, passcode, is_manager=False):
        employee = self.model(
            employee_id=employee_id,
            name=name,
            passcode=passcode,
            is_manager=is_manager
        )
        employee.save(using=self._db)
        return employee

    def create_manager(self, employee_id, name, passcode):
        return self.create_employee(employee_id, name, passcode, is_manager=True)

class Employee(AbstractBaseUser):
    employee_id = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=100)
    passcode = models.CharField(max_length=6)
    is_manager = models.BooleanField(default=False)

    objects = EmployeeManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name
