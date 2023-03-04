from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render,redirect
import mysql.connector as sql
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import base64
from PIL import Image
import io


# Create your views here.
id=''
pas=''
usrtype= ''

m=sql.connect(host="localhost",user="root",passwd="",database="hospital")
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
                request.session['id'] = id
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

    c.execute("select users.First_Name, users.Last_Name from users where users.EmployeeID="+id)
    details= c.fetchall()

    c.execute("select * from users")
    results = c.fetchall()
    result = {"staff": results, "details": details}

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
    c.execute("select users.First_Name, users.Last_Name from users where users.EmployeeID=" + id)
    details = c.fetchall()

    docid = request.session['id']
    querypend = "select patient.SSN,patient.First_Name,patient.Last_Name,appointment.AppointmentDT from patient inner join appointment on patient.SSN=appointment.PatientID where appointment.DoctorID="+docid+" and appointment.AppointmentDT > now();"
    c.execute(querypend)
    patlist = c.fetchall()

    query="select patient.SSN,patient.First_Name,patient.Last_Name,prescription.TreatmentPres from patient inner join prescription on prescription.DoctorID="+docid+" and patient.SSN=prescription.PatientID;"
    c.execute(query)
    patlist1 = c.fetchall()

    patinfo = []

    if request.method == 'POST' and request.POST.get("form_type") == 'info':
        patSSN = request.POST.get("patient-id")
        if patSSN == '':
            messages.error(request, 'Please fill Patient ID!')
            return redirect('doctor')
        testquery = "select * from tests where tests.PatientID="+patSSN+";"
        c.execute(testquery)
        pattest = c.fetchall()

        attach = "select tests.Attachments from tests where tests.PatientID="+patSSN+";"
        c.execute(attach)
        attachlist = c.fetchall()
        # encode all attachments
        #print(len(attachlist))
        imgbs64 = [None] * len(attachlist)
        for i in range(len(attachlist)):
            if attachlist[i][0] is not None:
                imgbs64[i] = base64.b64encode(attachlist[i][0]).decode('utf-8')

        context = [None] * len(attachlist)
        k=0
        for ida in imgbs64:
            if i is not None:
                context[k] = f'data:image/png;base64,{ida}'
            else:
                context[k] = None
            k=k+1


        if patSSN == '':
            messages.error(request, 'Please fill Patient ID!')
            return redirect('doctor')
        c.execute("select * from patient where SSN='"+patSSN+"'")
        patinfo = c.fetchall()

        if patinfo == []:
            result = {"pendpatient": patlist, "allpatient": patlist1, "patinfo": ["Patient Not Found"], "patpres": [], "details": details}
            return redirect(request,'doctor', result)
        else:
            c.execute("select * from prescription where PatientID='"+patSSN+"' and DoctorID='"+docid+"'")
            patpres = c.fetchall()

            if patpres == []:
                result = {"pendpatient": patlist, "allpatient": patlist1, "patinfo": patinfo, "patpres": ["No Prescription Found"], "pattest": pattest, "context": context, "details": details}
                return render(request, 'doctor.html', result)

            else:
                result = {"pendpatient": patlist, "allpatient": patlist1, "patinfo": patinfo, "patpres": patpres, "pattest": pattest, "context": context, "details": details}
                return render(request, 'doctor.html', result)

    result = {"pendpatient": patlist, "allpatient": patlist1, "patinfo": patinfo, "details": details}

    return render(request,'doctor.html', result)


def frontdesk(request):
    c.execute("select users.First_Name, users.Last_Name from users where users.EmployeeID=" + id)
    details = c.fetchall()

    c.execute("select * from patient inner join admit on patient.SSN=admit.PatientID where admit.Admit_Status=false")
    patlist = c.fetchall()

    c.execute("select * from room")
    roomlist = c.fetchall()

    c.execute("select * from patient")
    allpatlist = c.fetchall()

    c.execute("select patient.SSN,patient.First_Name,patient.Last_Name from patient inner join admit on patient.SSN=admit.PatientID where admit.Admit_Status=true")
    dispatlist = c.fetchall()

    c.execute(" select users.EmployeeID,users.First_Name,users.Last_Name,users.Specialization from users where users.type='doctor';")
    doclist = c.fetchall()

    result = {"patient": patlist, "room": roomlist, "dispat": dispatlist, "doc": doclist, "allpat": allpatlist,"details": details}

    if request.method == 'POST' and request.POST.get("form_type") == 'regpat':

        patSSN = request.POST.get("SSNID")
        pfName = request.POST.get("f_name")
        plName = request.POST.get("l_name")
        pDOB = request.POST.get("dob")
        pgender = request.POST.get("gender")

        if patSSN == '' or pfName == '' or plName == '' or pDOB == '' or pgender == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('frontdesk')
        else:
            c.execute("insert into patient values('"+patSSN+"','"+pfName+"','"+plName+"','"+pDOB+"','"+pgender+"')")
            m.commit()
            query = """INSERT INTO admit (PatientID, Admit_Status) VALUES (%s,%s)"""
            values = (patSSN, False)
            c.execute(query, values)
            m.commit()
            messages.success(request, 'Patient registered successfully!')
            return redirect('frontdesk')

    elif request.method == 'POST' and request.POST.get("form_type") == 'admitpat':
        patid= request.POST.get("patient")
        roomid = request.POST.get("room")

        if patid == '' or roomid == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('frontdesk')

        else:
            c.execute("select * from admit where PatientID='"+patid+"'")
            data = c.fetchall()
            if data:
                c.execute("update admit set RoomID='"+roomid+"' where admit.PatientID= "+patid)
                c.execute("update admit set Admit_Status=true where admit.PatientID= "+patid)
                c.execute("update room set Current_Capacity=Current_Capacity-1 where RoomID='" + roomid + "' and Current_Capacity>=0")
                m.commit()
                messages.success(request, 'Patient admitted successfully!')
            else:
                c.execute("insert into admit values('" + patid + "','" + roomid + "',True)")
                c.execute("update room set Current_Capacity=Current_Capacity-1 where RoomID='"+roomid+"' and Current_Capacity>=0")
                m.commit()
                messages.success(request, 'Patient admitted successfully!')
            return redirect('frontdesk')

    elif request.method == 'POST' and request.POST.get("form_type") == 'dispat':
        patid= str(request.POST.get("patient"))
        c.execute("select room.RoomID from room inner join admit on room.RoomID=admit.RoomID where admit.PatientID="+patid+";")
        roomid = c.fetchall()

        if patid == '' or roomid == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('frontdesk')

        else:
            rid = str(roomid[0][0])
            c.execute("update admit set Admit_Status=False where PatientID="+patid+" and RoomID="+rid+";")
            c.execute("update room set Current_Capacity=Current_Capacity+1 where RoomID="+rid+";")
            m.commit()
            messages.success(request, 'Patient discharged successfully!')
            return redirect('frontdesk')

    elif request.method == 'POST' and request.POST.get("form_type") == 'appoform':
        patid= str(request.POST.get("patient"))
        docid = str(request.POST.get("doctor"))
        appodate = str(request.POST.get("date"))
        appotime = str(request.POST.get("time"))

        appodt= appodate + " " + appotime

        print(patid,docid,appodt)

        if patid == '' or docid == '' or appodt == '' :
            messages.error(request, 'Please fill all the fields!')
            return redirect('frontdesk')

        else:
            c.execute("insert into appointment values('"+patid+"','"+docid+"','"+appodt+"')")
            m.commit()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('frontdesk')

    elif request.method == 'POST' and request.POST.get("form_type") == 'testform':
        testid = str(request.POST.get("testid"))
        patid = str(request.POST.get("patient"))
        testnd = str(request.POST.get("test"))
        testdate = str(request.POST.get("date"))
        testtime = str(request.POST.get("time"))

        testdt = testdate + " " + testtime

        if patid == '' or testnd == '' or testdt == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('frontdesk')

        else:
            query = """INSERT INTO tests (TestID,PatientID, TestDT, TestDesc) VALUES (%s,%s, %s, %s)"""
            values = (testid,patid, testdt, testnd)
            c.execute(query, values)
            m.commit()
            messages.success(request, 'Test booked successfully!')
            return redirect('frontdesk')

    return render(request,'front_desk.html', result);

def dataoperator(request):
    c.execute("select users.First_Name, users.Last_Name from users where users.EmployeeID=" + id)
    details = c.fetchall()

    c.execute("select * from tests")
    testlist = c.fetchall()

    c.execute("select * from patient")
    patlist = c.fetchall()

    c.execute("select users.EmployeeID,users.First_Name,users.Last_Name,users.Specialization from users where users.type='doctor'")
    doclist = c.fetchall()


    result = {'tstlist': testlist, "patient": patlist, "doctor": doclist , "details": details}

    if request.method == 'POST' and request.POST.get("form_type") == 'testform':
        testid = str(request.POST.get("test-select"))
        testres= str(request.POST.get("result-input"))
        imgfile = request.FILES.get("attachment-input")

        if testid == '' or testres == '' or imgfile == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('dataoperator')

        else:
            query = "UPDATE tests SET ResultDesc = %s, Attachments = %s WHERE TestID = %s"
            values = (testres, imgfile.read() , testid)
            c.execute(query, values)
            m.commit()
            messages.success(request, 'Test Results Updated!!!')
            return redirect('dataoperator')

    elif request.method == 'POST' and request.POST.get("form_type") == 'treatform':
        patid = str(request.POST.get("patient-select"))
        docid = str(request.POST.get("doctor-select"))
        treamnt = str(request.POST.get("treatment-input"))
        #print(patid,docid,treamnt)

        if patid == '' or docid == '' or treamnt == '':
            messages.error(request, 'Please fill all the fields!')
            return redirect('dataoperator')

        else:
            query = """INSERT INTO prescription (PatientID, DoctorID, TreatmentPres) VALUES (%s, %s, %s)"""
            values = (patid, docid, treamnt)
            c.execute(query, values)
            m.commit()
            messages.success(request, 'Treatment Prescribed!!!')

    return render(request,'data_operator.html', result);



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

