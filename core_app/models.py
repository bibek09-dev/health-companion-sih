from django.db import models
class patient(models.Model):
    unique_id = models.CharField(max_length=50, unique=True) # e.g. P-9021
    full_name = models.CharField(max_length=150)
    dob = models.CharField(max_length=50) # e.g. April 12, 1965
    passcode = models.CharField(max_length=255, default="patient123")
    compliance_rate = models.IntegerField(default=95)

    class Meta:
        db_table = 'mysite_patient'

    def str(self):
        return f"{self.full_name} ({self.unique_id})"
class doctor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=150)
    professional_data_link = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'mysite_doctor'

    def str(self):
        return self.name

class medication(models.Model):
    unique_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    dosage_standard = models.CharField(max_length=100)
    target_disease = models.CharField(max_length=150, default="General")
    description = models.TextField(blank=True)
    alternatives = models.TextField(blank=True)

    class Meta:
        db_table = 'mysite_medication'

    def str(self):
        return f"{self.name} (Treats: {self.target_disease})"

class Prescription(models.Model):
    # 🎯 Using matching lowercase string names to clear the relationship errors cleanly!
    doctor = models.ForeignKey('doctor', on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)
    prescribed_meds = models.ManyToManyField('medication', db_table='mysite_prescription_meds')
    pack_unique_id = models.CharField(max_length=100)
    ai_approval_status = models.CharField(max_length=50, default="PENDING")
    patient = models.ForeignKey('patient', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'mysite_prescription'