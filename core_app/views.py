from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Doctor, Medication, Prescription
from .ai_service import MedicationAnalyzer
from django.db import connection

def home_page(request):
    patient_info = {
        'id': 1,
        'full_name': 'Rajesh Kumar',
        'unique_id': 'P-9021',
        'dob': 'April 12, 1965'
    }
    
    is_doctor_logged_in = request.session.get('is_doc_authenticated', False)
    logged_in_doc_id = request.session.get('authenticated_doc_id', None)
    
    active_doctor = None
    if is_doctor_logged_in and logged_in_doc_id:
        active_doctor = Doctor.objects.filter(id=logged_in_doc_id).first()

    doctors = Doctor.objects.all()
    medications = Medication.objects.all()
    
    context = {
        'patient': patient_info,
        'doctors': doctors,
        'medications': medications,
        'is_logged_in': is_doctor_logged_in,
        'active_doctor': active_doctor,
    }
    
    if request.method == "POST" and "submit_prescription" in request.POST:
        if not is_doctor_logged_in:
            return JsonResponse({"status": "ERROR", "guide": "Unauthorized operation block."})
            
        med_ids = request.POST.getlist('med_ids')
        current_diagnosis = request.POST.get('active_diagnosis', '').strip()
        
        try:
            meds_to_analyze = Medication.objects.filter(id__in=med_ids)
            analyzer = MedicationAnalyzer()
            report = analyzer.analyze(patient_info, meds_to_analyze, current_diagnosis)
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO core_app_prescription (pack_unique_id, ai_approval_status, date_issued, doctor_id, patient_id_string) VALUES (%s, %s, datetime('now'), %s, %s)",
                    ["PACK-TEMP-123", report['status'], logged_in_doc_id, patient_info['unique_id']]
                )
                prescription_id = cursor.lastrowid
                
                for med_id in med_ids:
                    cursor.execute(
                        "INSERT INTO core_app_prescription_prescribed_meds (prescription_id, medication_id) VALUES (%s, %s)",
                        [prescription_id, med_id]
                    )
            
            return JsonResponse(report)
        except Exception as e:
            return JsonResponse({"status": "ERROR", "guide": str(e)})

    return render(request, 'index.html', context)

def doctor_login_view(request):
    if request.method == "POST":
        doctor_id = request.POST.get('doctor_id')
        passcode = request.POST.get('doctor_passcode')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT professional_data_link FROM mysite_doctor WHERE id = %s", 
                [doctor_id]
            )
            row = cursor.fetchone()
            
            if row and row[0] == passcode:
                request.session['is_doc_authenticated'] = True
                request.session['authenticated_doc_id'] = doctor_id
    return redirect('/')

def doctor_logout_view(request):
    request.session['is_doc_authenticated'] = False
    request.session['authenticated_doc_id'] = None
    return redirect('/')

def add_doctor_view(request):
    if request.method == "POST":
        name = request.POST.get('doc_name')
        specialty = request.POST.get('specialty')
        password = request.POST.get('doc_password')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mysite_doctor (name, specialty, professional_data_link) VALUES (%s, %s, %s)",
                [name, specialty, password]
            )
    return redirect('/')

def add_medication_view(request):
    if request.method == "POST":
        name = request.POST.get('med_name')
        uid = request.POST.get('med_uid')
        dosage = request.POST.get('dosage')
        target_disease = request.POST.get('target_disease')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO mysite_medication (unique_id, name, dosage_standard, target_disease, description, alternatives) VALUES (%s, %s, %s, %s, 'Authorized formulation item.', '')",
                [uid, name, dosage, target_disease]
            )
    return redirect('/')