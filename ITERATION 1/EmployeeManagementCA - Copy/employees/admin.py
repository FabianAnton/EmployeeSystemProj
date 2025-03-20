from django.contrib import admin
from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'is_manager')
    exclude = ('password',)

admin.site.register(Employee, EmployeeAdmin)
