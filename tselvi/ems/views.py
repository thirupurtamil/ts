#from turtle import pos
import django
from django.shortcuts import redirect, render
from .models import *
from django.contrib import messages 

# Create your views here.
def home(request):
    emp_data = Employee.objects.filter()
    on_leave = emp_data.filter(on_leave=True)
    d = {'total_employee':emp_data.count(), 'on_leave':on_leave.count()}
    return render(request, 'ems/dashboard.html',d)

def createEmployeee(request):
    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        doj = request.POST['doj']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        department = request.POST['department']
        post = request.POST['post']
        emp_obj = Employee.objects.create(name=name,dob=dob,doj=doj,address=address,city=city,state=state,zipcode=zipcode,country=country,department=department,post=post)
        messages.success(request, "Employee created successfully")
        return redirect('employee_list')
    return render(request, 'ems/create_employeee.html')

def employee_list(request):
    emp_data = Employee.objects.filter()
    d = {'employee':emp_data}
    return render(request, 'ems/employee_list.html',d)

def edit_employee(request, pid):
    emp_data =Employee.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        dob = request.POST['dob']
        doj = request.POST['doj']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        department = request.POST['department']
        post = request.POST['post']
        emp_obj = Employee.objects.filter(id=pid).update(name=name,dob=dob,doj=doj,address=address,city=city,state=state,zipcode=zipcode,country=country,department=department,post=post)
        messages.success(request, "Employee Updated successfully")
        return redirect('employee_list')
    return render(request, 'ems/edit_employeee.html', {'emp_data':emp_data})

def delete_employee(request, pid):
    data = Employee.objects.get(id=pid)
    data.delete()
    messages.success(request, "Employee Deleted successfully")
    return redirect('ems/employee_list')

def leave_status(request, pid):
    data = Employee.objects.get(id=pid)
    if data.on_leave:
        data.on_leave = False
    else:
        data.leave_count = data.leave_count + 1
        data.on_leave = True
    data.save()
    messages.success(request, "Employee leave status Changed successfully.")
    return redirect('employee_list')
