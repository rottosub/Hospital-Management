from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import date, timedelta
from django.http import JsonResponse, HttpResponse
from django.db import transaction

from .models import (
    CustomUser, DoctorProfile, DoctorAvailability, PatientProfile,
    Appointment, MedicalRecord, Prescription, Department,
    HospitalService, InventoryItem, Bill, BillItem
)
from .forms import (
    CustomUserCreationForm, DoctorProfileForm, DoctorAvailabilityForm,
    PatientProfileForm, AppointmentForm, MedicalRecordForm, PrescriptionForm,
    DepartmentForm, HospitalServiceForm, InventoryItemForm, BillForm, BillItemForm
)
from .mixins import AdminRequiredMixin, DoctorRequiredMixin, PatientRequiredMixin


# ==================== Authentication Views ====================

def register_view(request):
    """User Registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Requires admin approval
            user.save()
            
            # Create profile based on role
            if user.role == 'DOCTOR':
                DoctorProfile.objects.create(user=user)
            elif user.role == 'PATIENT':
                PatientProfile.objects.create(user=user)
            
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """Custom Login View"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_approved:
                messages.error(request, 'Your account is pending approval. Please wait for admin approval.')
                return render(request, 'core/login.html')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


@login_required
def dashboard_view(request):
    """Role-based Dashboard Redirect"""
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.is_doctor():
        return redirect('doctor_dashboard')
    elif request.user.is_patient():
        return redirect('patient_dashboard')
    else:
        messages.warning(request, 'Your account is pending approval.')
        return render(request, 'core/pending_approval.html')


# ==================== Admin Portal Views ====================

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'core/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Statistics
        context['total_patients'] = CustomUser.objects.filter(role='PATIENT', is_approved=True).count()
        context['total_doctors'] = CustomUser.objects.filter(role='DOCTOR', is_approved=True).count()
        context['pending_approvals'] = CustomUser.objects.filter(is_approved=False).count()
        context['today_appointments'] = Appointment.objects.filter(appointment_date=today).count()
        context['low_stock_items'] = InventoryItem.objects.filter(current_stock__lte=F('reorder_level')).count()
        
        # Recent appointments
        context['recent_appointments'] = Appointment.objects.all()[:10]
        
        # Pending approvals
        context['pending_users'] = CustomUser.objects.filter(is_approved=False)[:5]
        
        # Low stock alerts
        context['low_stock'] = InventoryItem.objects.filter(current_stock__lte=F('reorder_level'))[:5]
        
        # Revenue (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        context['revenue'] = Bill.objects.filter(
            bill_date__gte=thirty_days_ago,
            status='PAID'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        
        return context


class UserManagementView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'core/admin/user_management.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-date_joined')
        role_filter = self.request.GET.get('role')
        approval_filter = self.request.GET.get('approved')
        
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        if approval_filter == 'pending':
            queryset = queryset.filter(is_approved=False)
        elif approval_filter == 'approved':
            queryset = queryset.filter(is_approved=True)
        
        return queryset


@login_required
def approve_user(request, user_id):
    """Approve or reject user"""
    if not request.user.is_admin():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            user.is_approved = True
            user.save()
            messages.success(request, f'{user.username} has been approved.')
        elif action == 'reject':
            user.delete()
            messages.success(request, f'{user.username} has been rejected and deleted.')
    
    return redirect('user_management')


class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = 'core/admin/departments.html'
    context_object_name = 'departments'


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'core/admin/department_form.html'
    success_url = reverse_lazy('department_list')


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'core/admin/department_form.html'
    success_url = reverse_lazy('department_list')


class DepartmentDeleteView(AdminRequiredMixin, DeleteView):
    model = Department
    template_name = 'core/admin/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')


class InventoryListView(AdminRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'core/admin/inventory.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        low_stock = self.request.GET.get('low_stock')
        if low_stock == 'true':
            queryset = queryset.filter(current_stock__lte=F('reorder_level'))
        return queryset


class InventoryCreateView(AdminRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'core/admin/inventory_form.html'
    success_url = reverse_lazy('inventory_list')


class InventoryUpdateView(AdminRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'core/admin/inventory_form.html'
    success_url = reverse_lazy('inventory_list')


class HospitalServiceListView(AdminRequiredMixin, ListView):
    model = HospitalService
    template_name = 'core/admin/services.html'
    context_object_name = 'services'


class HospitalServiceCreateView(AdminRequiredMixin, CreateView):
    model = HospitalService
    form_class = HospitalServiceForm
    template_name = 'core/admin/service_form.html'
    success_url = reverse_lazy('service_list')


class HospitalServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = HospitalService
    form_class = HospitalServiceForm
    template_name = 'core/admin/service_form.html'
    success_url = reverse_lazy('service_list')


class AppointmentListView(AdminRequiredMixin, ListView):
    model = Appointment
    template_name = 'core/admin/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Appointment.objects.all().select_related('patient', 'doctor')
        status_filter = self.request.GET.get('status')
        date_filter = self.request.GET.get('date')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_filter:
            queryset = queryset.filter(appointment_date=date_filter)
        
        return queryset.order_by('-appointment_date', '-appointment_time')


class BillListView(AdminRequiredMixin, ListView):
    model = Bill
    template_name = 'core/admin/bills.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Bill.objects.all().select_related('patient')
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-bill_date')


class BillCreateView(AdminRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'core/admin/bill_form.html'
    success_url = reverse_lazy('bill_list')


class BillDetailView(AdminRequiredMixin, DetailView):
    model = Bill
    template_name = 'core/admin/bill_detail.html'
    context_object_name = 'bill'


@login_required
def add_bill_item(request, bill_id):
    """Add item to bill"""
    if not request.user.is_admin():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    bill = get_object_or_404(Bill, id=bill_id)
    
    if request.method == 'POST':
        form = BillItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.bill = bill
            item.save()
            messages.success(request, 'Item added to bill.')
            return redirect('bill_detail', pk=bill.id)
    else:
        form = BillItemForm()
    
    return render(request, 'core/admin/bill_item_form.html', {'form': form, 'bill': bill})


# ==================== Doctor Portal Views ====================

class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'core/doctor/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        doctor = self.request.user
        
        # Today's appointments
        context['today_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('appointment_time')
        
        # Upcoming appointments (next 7 days)
        week_from_now = today + timedelta(days=7)
        context['upcoming_appointments'] = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            appointment_date__lte=week_from_now,
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('appointment_date', 'appointment_time')[:10]
        
        # Assigned inpatients
        context['inpatients'] = PatientProfile.objects.filter(
            admission_status='INPATIENT',
            user__appointments__doctor=doctor
        ).distinct()[:10]
        
        # Recent medical records
        context['recent_records'] = MedicalRecord.objects.filter(
            doctor=doctor
        ).order_by('-record_date')[:5]
        
        return context


class DoctorAppointmentListView(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'core/doctor/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        return Appointment.objects.filter(
            doctor=self.request.user
        ).order_by('-appointment_date', '-appointment_time')


@login_required
def update_appointment_status(request, appointment_id):
    """Update appointment status (approve/reschedule/cancel)"""
    if not request.user.is_doctor():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            appointment.status = 'CONFIRMED'
            appointment.save()
            messages.success(request, 'Appointment confirmed.')
        elif action == 'cancel':
            appointment.status = 'CANCELLED'
            appointment.save()
            messages.success(request, 'Appointment cancelled.')
        elif action == 'reschedule':
            appointment.appointment_date = request.POST.get('new_date')
            appointment.appointment_time = request.POST.get('new_time')
            appointment.status = 'PENDING'
            appointment.save()
            messages.success(request, 'Appointment rescheduled.')
    
    return redirect('doctor_appointments')


class DoctorPatientListView(DoctorRequiredMixin, ListView):
    template_name = 'core/doctor/patients.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def get_queryset(self):
        # Get patients who have appointments with this doctor
        return CustomUser.objects.filter(
            role='PATIENT',
            appointments__doctor=self.request.user
        ).distinct()


class MedicalRecordListView(DoctorRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'core/doctor/medical_records.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        patient_id = self.request.GET.get('patient')
        queryset = MedicalRecord.objects.filter(doctor=self.request.user)
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.order_by('-record_date')


class MedicalRecordCreateView(DoctorRequiredMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'core/doctor/medical_record_form.html'
    success_url = reverse_lazy('doctor_medical_records')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.doctor = self.request.user
        return super().form_valid(form)


class MedicalRecordDetailView(DoctorRequiredMixin, DetailView):
    model = MedicalRecord
    template_name = 'core/doctor/medical_record_detail.html'
    context_object_name = 'record'
    
    def get_queryset(self):
        return MedicalRecord.objects.filter(doctor=self.request.user)


@login_required
def add_prescription(request, record_id):
    """Add prescription to medical record"""
    if not request.user.is_doctor():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    record = get_object_or_404(MedicalRecord, id=record_id, doctor=request.user)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.medical_record = record
            prescription.save()
            messages.success(request, 'Prescription added.')
            return redirect('doctor_medical_record_detail', pk=record.id)
    else:
        form = PrescriptionForm()
    
    return render(request, 'core/doctor/prescription_form.html', {'form': form, 'record': record})


class DoctorAvailabilityListView(DoctorRequiredMixin, ListView):
    model = DoctorAvailability
    template_name = 'core/doctor/availability.html'
    context_object_name = 'availabilities'
    
    def get_queryset(self):
        try:
            doctor_profile = self.request.user.doctor_profile
            return DoctorAvailability.objects.filter(doctor=doctor_profile)
        except DoctorProfile.DoesNotExist:
            return DoctorAvailability.objects.none()


class DoctorAvailabilityCreateView(DoctorRequiredMixin, CreateView):
    model = DoctorAvailability
    form_class = DoctorAvailabilityForm
    template_name = 'core/doctor/availability_form.html'
    success_url = reverse_lazy('doctor_availability')
    
    def form_valid(self, form):
        try:
            doctor_profile = self.request.user.doctor_profile
        except DoctorProfile.DoesNotExist:
            messages.error(self.request, 'Please complete your doctor profile first.')
            return redirect('doctor_profile_edit')
        
        form.instance.doctor = doctor_profile
        return super().form_valid(form)


# ==================== Patient Portal Views ====================

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = 'core/patient/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        patient = self.request.user
        
        # Upcoming appointments
        context['upcoming_appointments'] = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('appointment_date', 'appointment_time')[:5]
        
        # Recent appointments
        context['recent_appointments'] = Appointment.objects.filter(
            patient=patient
        ).order_by('-appointment_date')[:5]
        
        # Recent medical records
        context['recent_records'] = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-record_date')[:5]
        
        # Pending bills
        context['pending_bills'] = Bill.objects.filter(
            patient=patient,
            status__in=['PENDING', 'PARTIAL']
        ).order_by('-bill_date')[:5]
        
        return context


class PatientAppointmentListView(PatientRequiredMixin, ListView):
    model = Appointment
    template_name = 'core/patient/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user
        ).order_by('-appointment_date', '-appointment_time')


class PatientAppointmentCreateView(PatientRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'core/patient/appointment_form.html'
    success_url = reverse_lazy('patient_appointments')
    
    def form_valid(self, form):
        form.instance.patient = self.request.user
        form.instance.status = 'PENDING'
        messages.success(self.request, 'Appointment requested. Please wait for doctor confirmation.')
        return super().form_valid(form)


class PatientMedicalRecordListView(PatientRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'core/patient/medical_records.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        return MedicalRecord.objects.filter(
            patient=self.request.user
        ).order_by('-record_date')


class PatientMedicalRecordDetailView(PatientRequiredMixin, DetailView):
    model = MedicalRecord
    template_name = 'core/patient/medical_record_detail.html'
    context_object_name = 'record'
    
    def get_queryset(self):
        return MedicalRecord.objects.filter(patient=self.request.user)


class PatientBillListView(PatientRequiredMixin, ListView):
    model = Bill
    template_name = 'core/patient/bills.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        return Bill.objects.filter(
            patient=self.request.user
        ).order_by('-bill_date')


class PatientBillDetailView(PatientRequiredMixin, DetailView):
    model = Bill
    template_name = 'core/patient/bill_detail.html'
    context_object_name = 'bill'
    
    def get_queryset(self):
        return Bill.objects.filter(patient=self.request.user)


# ==================== Profile Management ====================

@login_required
def doctor_profile_edit(request):
    """Edit doctor profile"""
    if not request.user.is_doctor():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    try:
        profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        profile = DoctorProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=profile)
    
    return render(request, 'core/doctor/profile_edit.html', {'form': form})


@login_required
def patient_profile_edit(request):
    """Edit patient profile"""
    if not request.user.is_patient():
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = PatientProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=profile)
    
    return render(request, 'core/patient/profile_edit.html', {'form': form})
