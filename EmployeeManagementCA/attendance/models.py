from django.db import models
from django.utils.timezone import now
from employees.models import Employee

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    break_start_time = models.DateTimeField(null=True, blank=True)
    break_end_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

    def is_on_break(self):
        """Returns True if the employee has started a break but not ended it yet."""
        return self.break_start_time is not None and self.break_end_time is None

    def is_clocked_in(self):
        """Check if employee has clocked in but not out yet."""
        return self.clock_in_time is not None and self.clock_out_time is None
