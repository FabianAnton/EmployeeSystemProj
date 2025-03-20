from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'clock_in_time', 'clock_out_time', 'break_start_time', 'break_end_time')
    list_filter = ('date', 'employee')

admin.site.register(Attendance, AttendanceAdmin)
