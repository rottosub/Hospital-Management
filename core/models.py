from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class CustomUser(AbstractUser):
    """Custom User Model with Role-based Access Control"""
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    is_approved = models.BooleanField(default=False)  # For admin approval
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'ADMIN' and self.is_approved
    
    def is_doctor(self):
        return self.role == 'DOCTOR' and self.is_approved
    
    def is_patient(self):
        return self.role == 'PATIENT' and self.is_approved


class Department(models.Model):
    """Hospital Departments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_headed',
        limit_choices_to={'role': 'DOCTOR'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    """Doctor Profile Information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"


class DoctorAvailability(models.Model):
    """Doctor's Availability Schedule"""
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name() or self.doctor.user.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class PatientProfile(models.Model):
    """Patient Profile Information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    ADMISSION_STATUS_CHOICES = [
        ('OUTPATIENT', 'Outpatient'),
        ('INPATIENT', 'Inpatient'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relation = models.CharField(max_length=50)
    admission_status = models.CharField(max_length=10, choices=ADMISSION_STATUS_CHOICES, default='OUTPATIENT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_admission_status_display()}"
    
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Appointment(models.Model):
    """Patient Appointments"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('OPD', 'OPD'),
        ('FOLLOWUP', 'Follow-up'),
        ('CONSULTATION', 'Consultation'),
        ('CHECKUP', 'Checkup'),
    ]
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'role': 'PATIENT'})
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'role': 'DOCTOR'})
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    appointment_type = models.CharField(max_length=15, choices=APPOINTMENT_TYPE_CHOICES, default='OPD')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
    
    def __str__(self):
        return f"{self.patient.get_full_name() or self.patient.username} with Dr. {self.doctor.get_full_name() or self.doctor.username} on {self.appointment_date}"


class MedicalRecord(models.Model):
    """Electronic Health Records (EHR)"""
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='medical_records', limit_choices_to={'role': 'PATIENT'})
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_records', limit_choices_to={'role': 'DOCTOR'})
    record_date = models.DateTimeField(default=timezone.now)
    diagnosis = models.TextField()
    treatment_notes = models.TextField()
    symptoms = models.TextField(blank=True)
    # Vitals
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    heart_rate = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    # Additional fields
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-record_date']
    
    def __str__(self):
        return f"Record for {self.patient.get_full_name() or self.patient.username} on {self.record_date.date()}"


class Prescription(models.Model):
    """Prescriptions linked to Medical Records"""
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)  # e.g., "500mg", "1 tablet"
    frequency = models.CharField(max_length=100)  # e.g., "Twice daily", "After meals"
    duration = models.CharField(max_length=100)  # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} ({self.frequency})"


class HospitalService(models.Model):
    """Hospital Services and their Costs"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ${self.cost}"


class InventoryItem(models.Model):
    """Hospital Inventory Management"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    current_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=50, default='unit')  # e.g., "box", "bottle", "pack"
    supplier = models.CharField(max_length=200, blank=True)
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - Stock: {self.current_stock} {self.unit}"
    
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level


class Bill(models.Model):
    """Patient Bills/Invoices"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bills', limit_choices_to={'role': 'PATIENT'})
    bill_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-bill_date']
    
    def __str__(self):
        return f"Bill #{self.id} - {self.patient.get_full_name() or self.patient.username} - ${self.total_amount}"
    
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    def is_fully_paid(self):
        return self.paid_amount >= self.total_amount


class BillItem(models.Model):
    """Individual items in a Bill"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price} = ${self.total_price}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update bill total
        bill = self.bill
        bill.total_amount = sum(item.total_price for item in bill.items.all())
        bill.save()
