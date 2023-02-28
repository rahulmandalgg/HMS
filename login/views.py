from django.shortcuts import render,redirect
import mysql.connector as sql
from login.models import users
# Create your views here.

id=''
pas=''
usrtype= ''

m=sql.connect(host="localhost",user="root",passwd="mandal.1234",database="hospital")

def login(request):
    global id,pas,usrtype,m
    if request.method=="POST":
        c=m.cursor()
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

def admin(request):
    c = m.cursor()
    c.execute("select * from users")
    results = c.fetchall()
    #print(results)
    result = {"staff": results}
    return render(request,'admin.html',result)

def doctor(request):
    return render(request,'doctor.html')

def frontdesk(request):
    return render(request,'front_desk.html')

def dataoperator(request):
    return render(request,'data_operator.html')