from django.shortcuts import render,redirect
import mysql.connector as sql
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages


# Create your views here.

id=''
pas=''
usrtype= ''

m=sql.connect(host="localhost",user="root",passwd="mandal.1234",database="hospital")
c=m.cursor()
def login(request):
    global id,pas,usrtype,m,c
    if request.method=="POST":
        d=request.POST
        for key,value in d.items():
            if key=='EmployeeID':
                id=value
            if key=='Password':
                pas=value
        c.execute("select * from users where EmployeeID='"+id+"' and Password='"+pas+"'")
        data=c.fetchall()
        t=tuple(data)
        if t==():
            return render(request,'login.html',{'msg':'Invalid Credentials'})
        else:
            for i in data:
                usrtype=i[0]
            if len(data)>0:
                if usrtype== 'admin':
                    return redirect('admin')
                elif usrtype== 'doctor':
                    return redirect('doctor')
                elif usrtype== 'front desk operator':
                    return redirect('frontdesk')
                elif usrtype== 'data operator':
                    return redirect('dataoperator')
                else:
                    return render(request,'login.html',{'msg':'Invalid Credentials'})
            else:
                return render(request,'login.html',{'msg':'Invalid Credentials'})
    return render(request, 'login.html')

@csrf_protect
def admin(request):

    c = m.cursor()
    c.execute("select * from users")
    results = c.fetchall()
    result = {"staff": results}



    if request.method == 'POST' and request.POST.get("form_type") == 'rform':
        remove_id = request.POST.get("remove-user-id")
        if remove_id == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('admin')
        c.execute("delete from users where EmployeeID='"+remove_id+"'")
        m.commit()
        messages.success(request, 'User removed successfully!')
        return redirect('admin')

    elif request.method == 'POST' and request.POST.get("form_type") == 'addform':
        user_type = request.POST.get("type")
        first_name = request.POST.get("first-name")
        last_name = request.POST.get("last-name")
        employee_id = request.POST.get("employee-id")
        password = request.POST.get("password")

        if employee_id == '' or password == '' or first_name == '' or last_name == '' or user_type == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('admin')

        if user_type == 'doctor':
            specialization = request.POST.get("specialization")
            cert_given_date = request.POST.get("certificate-given-date")
            cert_expiry_date = request.POST.get("certificate-expiry-date")
            add_user_to_database(user_type, first_name, last_name, employee_id, password, specialization, cert_given_date,
                                 cert_expiry_date)
            return redirect('admin')
        else:
            add_user_to_database(user_type, first_name, last_name, employee_id, password)
            return redirect('admin')

    return render(request,'admin.html',result)

def doctor(request):
    return render(request,'doctor.html')

def frontdesk(request):
    return render(request,'front_desk.html')

def dataoperator(request):
    return render(request,'data_operator.html')

def add_user_to_database(user_type, first_name, last_name, employee_id, password,specialization=None, cert_given_date=None, cert_expiry_date=None):
    # Define the MySQL query
    if user_type == 'doctor':
        query = """INSERT INTO users (Type, First_Name, Last_Name, EmployeeID, Password, Specialization, CertificateGD, CertificateED)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (user_type, first_name, last_name, employee_id, password, specialization, cert_given_date, cert_expiry_date)
    else:
        query = """INSERT INTO users (Type, First_Name, Last_Name, EmployeeID, Password)
                   VALUES (%s, %s, %s, %s, %s)"""
        values = (user_type, first_name, last_name, employee_id, password)
    # Execute the query and commit the changes
    c.execute(query, values)
    m.commit()

def delete_user_from_database(employee_id):
    # Define the MySQL query
    query = """DELETE FROM users WHERE EmployeeID = %s"""
    values = (employee_id)

    # Execute the query and commit the changes
    c.execute(query, values)
    m.commit()