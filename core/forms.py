from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    CustomUser, DoctorProfile, DoctorAvailability, PatientProfile,
    Appointment, MedicalRecord, Prescription, Department,
    HospitalService, InventoryItem, Bill, BillItem
)


class CustomUserCreationForm(UserCreationForm):
    """User Registration Form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'class': 'form-select'})


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'license_number', 'phone', 'address', 'department', 'bio', 'consultation_fee']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'phone', 'address', 
                  'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation', 'admission_status']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_status': forms.Select(attrs={'class': 'form-select'}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter doctors to only approved doctors
        self.fields['doctor'].queryset = CustomUser.objects.filter(role='DOCTOR', is_approved=True)


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'diagnosis', 'treatment_notes', 'symptoms',
                  'blood_pressure_systolic', 'blood_pressure_diastolic', 'temperature',
                  'heart_rate', 'weight', 'height', 'follow_up_required', 'follow_up_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'treatment_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_doctor():
            # Doctors can only see their assigned patients
            self.fields['patient'].queryset = CustomUser.objects.filter(
                role='PATIENT',
                appointments__doctor=user,
                appointments__status__in=['CONFIRMED', 'COMPLETED']
            ).distinct()


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head_of_department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'head_of_department': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['head_of_department'].queryset = CustomUser.objects.filter(role='DOCTOR', is_approved=True)


class HospitalServiceForm(forms.ModelForm):
    class Meta:
        model = HospitalService
        fields = ['name', 'description', 'cost', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'current_stock', 'reorder_level', 'unit_price', 'unit', 'supplier']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['patient', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = CustomUser.objects.filter(role='PATIENT', is_approved=True)


class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

