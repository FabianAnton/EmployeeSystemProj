from django import forms
from django.contrib import admin
from .models import Employee, Department

class EmployeeAdminForm(forms.ModelForm):
    department_name = forms.CharField(
        max_length=100,
        label="Department Name",
        widget=forms.TextInput(attrs={'placeholder': 'Type department name'})
    )
    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'passcode', 'is_manager', 'department_name','profile_picture']

    def save(self, commit=True):

        department_name = self.cleaned_data['department_name']
        department, _ = Department.objects.get_or_create(Department_name=department_name)

        employee = super().save(commit=False)
        employee.department = department
        if commit:
            employee.save()
        return employee

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('employee_id','Department_name')

class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ('employee_id', 'name','department','is_manager')
    exclude = ('password',)

admin.site.register(Employee, EmployeeAdmin)
