# Hospital Management System

A comprehensive, secure, and responsive Hospital Management System built with Django, featuring three distinct user portals: Admin, Doctor, and Patient.

## Features

### 🔐 Authentication & User Management
- Custom User Model with role-based access (Admin, Doctor, Patient)
- User registration with admin approval workflow
- Secure login/logout functionality
- Role-based access control (RBAC)

### 👨‍💼 Admin Portal
- **Dashboard**: Overview of key metrics (patients, doctors, appointments, revenue)
- **User Management**: Approve/reject pending registrations, manage all users
- **Department Management**: CRUD operations for hospital departments
- **Inventory Management**: Track stock levels with low stock alerts
- **Service Management**: Manage hospital services and their costs
- **Appointment Management**: View and manage all hospital appointments
- **Billing**: Create and manage patient bills/invoices

### 🧑‍⚕️ Doctor Portal
- **Dashboard**: Today's appointments and assigned inpatients
- **Appointment Management**: View, confirm, and reschedule appointments
- **Patient Management**: Access assigned patients' information
- **Medical Records (EHR)**: Create and manage electronic health records
- **Prescriptions**: Add prescriptions to medical records
- **Availability Schedule**: Manage working hours and availability

### 🧍 Patient Portal
- **Dashboard**: Overview of appointments, records, and bills
- **Appointment Booking**: View doctor schedules and book appointments
- **Medical Records**: View and download personal medical records
- **Prescriptions**: Access prescription history
- **Billing**: View bills and payment status
- **Profile Management**: Update personal information

## Technology Stack

- **Backend**: Django 5.2.8
- **Frontend**: Bootstrap 5.3.0
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **Additional**: Django Widget Tweaks, Pillow (for image handling)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project
```bash
cd "E:\hospital management"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin user. Make sure to set the role as 'ADMIN' and approve the user.

### Step 7: Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Initial Setup

1. **Create Admin User**: Use `python manage.py createsuperuser` to create the first admin user
2. **Approve Admin**: In Django admin panel (`/admin/`), set `is_approved=True` for the admin user
3. **Create Departments**: Add hospital departments through the admin portal
4. **Add Services**: Configure hospital services and their costs
5. **Add Inventory Items**: Set up inventory items with reorder levels

## User Roles

### Admin
- Full system access
- User approval/rejection
- Resource management
- Financial reporting

### Doctor
- View assigned patients
- Create medical records
- Manage appointments
- Prescribe medications

### Patient
- Book appointments
- View medical records
- Check bills
- Manage profile

## Security Features

- **RBAC**: Role-Based Access Control using custom mixins
- **Login Required**: All views require authentication
- **Permission Checks**: Views verify user roles before access
- **Secure Password Handling**: Django's built-in password hashing
- **CSRF Protection**: Enabled by default

## Deployment

### Production Settings

For production deployment, update `settings.py`:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Set up proper database (PostgreSQL recommended)
4. Configure static files serving (use WhiteNoise or CDN)
5. Set up media files storage (AWS S3 recommended)
6. Use environment variables for `SECRET_KEY`
7. Configure HTTPS

### Using Gunicorn & Nginx

```bash
pip install gunicorn
gunicorn hospital_management.wsgi:application
```

## Project Structure

```
hospital_management/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions and classes
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin configuration
│   ├── mixins.py           # Custom mixins for RBAC
│   └── templates/          # HTML templates
│       ├── core/
│       │   ├── admin/      # Admin portal templates
│       │   ├── doctor/     # Doctor portal templates
│       │   └── patient/    # Patient portal templates
├── hospital_management/    # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── manage.py              # Django management script
├── requirements.txt        # Python dependencies
└── README.md             # This file
```

## Key Models

- **CustomUser**: Extended user model with roles
- **DoctorProfile**: Doctor-specific information
- **PatientProfile**: Patient-specific information
- **Appointment**: Patient appointments
- **MedicalRecord**: Electronic health records
- **Prescription**: Medication prescriptions
- **Department**: Hospital departments
- **InventoryItem**: Inventory management
- **HospitalService**: Service catalog
- **Bill**: Patient billing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

---

**Note**: This is a development version. For production use, ensure proper security configurations, database setup, and deployment practices.

