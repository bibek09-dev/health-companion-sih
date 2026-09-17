from django.db import models

class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=100)
    professional_data_link = models.URLField(blank=True) # Secure password slot

    class Meta:
        app_label = 'mysite'
        db_table = 'mysite_doctor'

    def str(self):
        return f"Dr. {self.name} ({self.specialty})"

class Medication(models.Model):
    unique_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    dosage_standard = models.CharField(max_length=100)
    target_disease = models.CharField(max_length=150, default='General') # 👈 NEW FIELD
    description = models.TextField(blank=True)
    alternatives = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'mysite'
        db_table = 'mysite_medication'

    def str(self):
        return f"{self.name} (Treats: {self.target_disease})"

class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)
    prescribed_meds = models.ManyToManyField(Medication, db_table='mysite_prescription_meds')
    pack_unique_id = models.CharField(max_length=100)
    ai_approval_status = models.CharField(max_length=50, default='PENDING')
    patient_id_string = models.CharField(max_length=50, default='P-9021')

    class Meta:
        app_label = 'mysite'
        db_table = 'mysite_prescription'
        