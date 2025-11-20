from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Admin Portal
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.UserManagementView.as_view(), name='user_management'),
    path('admin/users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('admin/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('admin/departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('admin/departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('admin/departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    path('admin/inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('admin/inventory/create/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('admin/inventory/<int:pk>/update/', views.InventoryUpdateView.as_view(), name='inventory_update'),
    path('admin/services/', views.HospitalServiceListView.as_view(), name='service_list'),
    path('admin/services/create/', views.HospitalServiceCreateView.as_view(), name='service_create'),
    path('admin/services/<int:pk>/update/', views.HospitalServiceUpdateView.as_view(), name='service_update'),
    path('admin/appointments/', views.AppointmentListView.as_view(), name='admin_appointments'),
    path('admin/bills/', views.BillListView.as_view(), name='bill_list'),
    path('admin/bills/create/', views.BillCreateView.as_view(), name='bill_create'),
    path('admin/bills/<int:pk>/', views.BillDetailView.as_view(), name='bill_detail'),
    path('admin/bills/<int:bill_id>/add-item/', views.add_bill_item, name='add_bill_item'),
    
    # Doctor Portal
    path('doctor/dashboard/', views.DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('doctor/appointments/', views.DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('doctor/appointments/<int:appointment_id>/update/', views.update_appointment_status, name='update_appointment_status'),
    path('doctor/patients/', views.DoctorPatientListView.as_view(), name='doctor_patients'),
    path('doctor/medical-records/', views.MedicalRecordListView.as_view(), name='doctor_medical_records'),
    path('doctor/medical-records/create/', views.MedicalRecordCreateView.as_view(), name='doctor_medical_record_create'),
    path('doctor/medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='doctor_medical_record_detail'),
    path('doctor/medical-records/<int:record_id>/prescription/', views.add_prescription, name='add_prescription'),
    path('doctor/availability/', views.DoctorAvailabilityListView.as_view(), name='doctor_availability'),
    path('doctor/availability/create/', views.DoctorAvailabilityCreateView.as_view(), name='doctor_availability_create'),
    path('doctor/profile/', views.doctor_profile_edit, name='doctor_profile_edit'),
    
    # Patient Portal
    path('patient/dashboard/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
    path('patient/appointments/', views.PatientAppointmentListView.as_view(), name='patient_appointments'),
    path('patient/appointments/create/', views.PatientAppointmentCreateView.as_view(), name='patient_appointment_create'),
    path('patient/medical-records/', views.PatientMedicalRecordListView.as_view(), name='patient_medical_records'),
    path('patient/medical-records/<int:pk>/', views.PatientMedicalRecordDetailView.as_view(), name='patient_medical_record_detail'),
    path('patient/bills/', views.PatientBillListView.as_view(), name='patient_bills'),
    path('patient/bills/<int:pk>/', views.PatientBillDetailView.as_view(), name='patient_bill_detail'),
    path('patient/profile/', views.patient_profile_edit, name='patient_profile_edit'),
]

