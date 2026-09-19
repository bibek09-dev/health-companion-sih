from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import doctor, medication, Prescription, patient
from .ai_service import MedicationAnalyzer

def home_page(request):
    doctors = doctor.objects.all()
    medications = medication.objects.all()
    
    active_role = request.session.get('role', None)
    active_user_id = request.session.get('user_id', None)
    
    active_user = None
    active_patient = None
    prescriptions = []
    
    if active_role == 'doctor' and active_user_id:
        active_user = doctor.objects.filter(id=active_user_id).first()
    elif active_role == 'patient' and active_user_id:
        # 🎯 Dynamic Profile Tracking extraction hook!
        active_patient = patient.objects.filter(id=active_user_id).first()
        # Filtering prescriptions by the dynamic patient foreign key relation link
        prescriptions = Prescription.objects.filter(patient_id=active_user_id).order_by('-date_issued')

    context = {
        'doctors': doctors,
        'medications': medications,
        'active_user': active_user,
        'patient': active_patient, # Pass the dynamic model directly to the front-end!
        'prescriptions': prescriptions,
    }
    
    # 4. Handle asynchronous post submission requests sent from the practitioner desk console
    if request.method == "POST" and "submit_prescription" in request.POST:
        if active_role != 'doctor':
            return JsonResponse({"status": "ERROR", "guide": "Unauthorized route block."})
            
        med_ids = request.POST.getlist('med_ids')
        current_diagnosis = request.POST.get('active_diagnosis', '').strip()
        
        try:
            meds_to_analyze = medication.objects.filter(id__in=med_ids)
            analyzer = MedicationAnalyzer()
            report = analyzer.analyze({}, meds_to_analyze, current_diagnosis)
            
            # Extract target inputs typed by the doctor in real-time
            target_name = request.POST.get('target_patient_name', '').strip()
            target_serial = request.POST.get('target_device_serial', '').strip()
            
            # Dynamic matching search lookup in database to bind the transaction record row safely
            target_patient_node = patient.objects.filter(full_name__iexact=target_name, unique_id__iexact=target_serial).first()
            
            # If patient record isn't in system database yet, auto-create a profile row on the fly!
            if not target_patient_node:
                target_patient_node = patient.objects.create(
                    full_name=target_name,
                    unique_id=target_serial,
                    dob="1970-01-01",
                    passcode="patient123",
                    compliance_rate=100
                )
            
            # Commit structural validation records into SQLite database engine keys
            prescription = Prescription.objects.create(
                doctor_id=active_user_id,
                pack_unique_id="BATCH-SCAN-VAL",
                ai_approval_status=report['status'],
                patient_id=target_patient_node.id  # 🎯 Linked straight to the dynamic profile row container!
            )
            prescription.prescribed_meds.set(meds_to_analyze)
            
            return JsonResponse(report)
        except Exception as e:
            return JsonResponse({"status": "ERROR", "guide": str(e)})

    return render(request, 'index.html', context)
    # ================= PART 2: DUAL-ROLE ROUTING AUTHENTICATION CONTROLLERS =================

def system_login_view(request):
    if request.method == "POST":
        role = request.POST.get('role')
        passcode = request.POST.get('passcode')
        
# 👤 THREE-FACTOR SECURE PATIENT AUTHENTICATION ROUTING HOOK
        if role == 'patient':
            input_name = request.POST.get('patient_name', '').strip()
            input_serial = request.POST.get('device_serial', '').strip()
            
            # Database multi-field logic trace verification loop matching security values
            user_node = patient.objects.filter(
                full_name__iexact=input_name,
                unique_id__iexact=input_serial,
                passcode=passcode
            ).first()
            
            if user_node:
                request.session['role'] = 'patient'
                request.session['user_id'] = user_node.id
                return redirect('/')
        elif role == 'doctor':
            doctor_id = request.POST.get('doctor_id')
            doc = doctor.objects.filter(id=doctor_id).first()
            if doc and doc.professional_data_link == passcode:
                request.session['role'] = 'doctor'
                request.session['user_id'] = doctor_id
                return redirect('/')
                
    return redirect('/')

def system_logout_view(request):
    request.session.flush() # Wipes all active session traces clean out of memory storage keys
    return redirect('/')
def add_patient_view(request):
    if request.method == "POST":
        name = request.POST.get('patient_name')
        uid = request.POST.get('patient_uid')
        dob = request.POST.get('dob')
        password = request.POST.get('patient_password')
        patient.objects.create(full_name=name, unique_id=uid, dob=dob, passcode=password, compliance_rate=100)
    return redirect('/')
# ================= DATA ENGINE REGISTRATION HANDLERS =================

def add_doctor_view(request):
    if request.method == "POST":
        name = request.POST.get('doc_name')
        specialty = request.POST.get('specialty')
        password = request.POST.get('doc_password')
        # Saves the practitioner profile straight into your dynamic database map rows
        doctor.objects.create(name=name, specialty=specialty, professional_data_link=password)
    return redirect('/')

def add_medication_view(request):
    if request.method == "POST":
        name = request.POST.get('med_name')
        uid = request.POST.get('med_uid')
        dosage = request.POST.get('dosage')
        target_disease = request.POST.get('target_disease')
        # Saves the medicine formulary stock straight into your database rows
        medication.objects.create(unique_id=uid, name=name, dosage_standard=dosage, target_disease=target_disease)
    return redirect('/')        