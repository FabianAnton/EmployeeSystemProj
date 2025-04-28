from datetime import timedelta

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
        """Returns True if the employee has started a break but has not ended it yet."""
        return self.break_start_time is not None and self.break_end_time is None

    def is_clocked_in(self):
        """Returns True if the employee has clocked in but not yet clocked out."""
        return self.clock_in_time is not None and self.clock_out_time is None

    def total_hours(self):
        """
        Calculates the total working hours for the day, excluding break time.
        Returns total hours in 'HH:MM' format or None if not clocked out.
        """
        if self.clock_in_time and self.clock_out_time:
            total_work_time = self.clock_out_time - self.clock_in_time
            break_duration = timedelta()

            if self.break_start_time and self.break_end_time:
                break_duration = self.break_end_time - self.break_start_time

            worked_time = total_work_time - break_duration
            total_minutes = int(worked_time.total_seconds() // 60)
            hours, minutes = divmod(total_minutes, 60)
            return f"{hours:02d}:{minutes:02d}"

        return None
