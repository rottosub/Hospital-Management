from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser, DoctorProfile, DoctorAvailability, PatientProfile,
    Appointment, MedicalRecord, Prescription, Department,
    HospitalService, InventoryItem, Bill, BillItem
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Hospital Management', {'fields': ('role', 'is_approved')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Hospital Management', {'fields': ('role', 'is_approved')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_of_department', 'created_at']
    search_fields = ['name']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'department', 'consultation_fee']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'specialization', 'license_number']
    list_filter = ['department', 'specialization']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['doctor__user__username']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'gender', 'blood_group', 'admission_status', 'phone']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    list_filter = ['gender', 'blood_group', 'admission_status']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'appointment_type']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['patient__username', 'doctor__username']
    date_hierarchy = 'appointment_date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'record_date', 'diagnosis', 'follow_up_required']
    list_filter = ['record_date', 'follow_up_required']
    search_fields = ['patient__username', 'doctor__username', 'diagnosis']
    date_hierarchy = 'record_date'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medical_record', 'medicine_name', 'dosage', 'frequency', 'duration']
    search_fields = ['medicine_name', 'medical_record__patient__username']


@admin.register(HospitalService)
class HospitalServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_stock', 'reorder_level', 'unit_price', 'is_low_stock', 'last_restocked']
    search_fields = ['name']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'bill_date', 'total_amount', 'paid_amount', 'status', 'remaining_amount']
    list_filter = ['status', 'bill_date']
    search_fields = ['patient__username']
    date_hierarchy = 'bill_date'
    inlines = [BillItemInline]
    
    def remaining_amount(self, obj):
        return obj.remaining_amount()
    remaining_amount.short_description = 'Remaining'
