"""
Script to create an initial admin user for the Hospital Management System.
Run this after migrations: python manage.py shell < setup_admin.py
Or use: python manage.py createsuperuser (then approve in admin panel)
"""

from core.models import CustomUser

# Create admin user
username = input("Enter admin username: ")
email = input("Enter admin email: ")
password = input("Enter admin password: ")

# Check if user exists
if CustomUser.objects.filter(username=username).exists():
    print(f"User {username} already exists!")
else:
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='ADMIN',
        is_approved=True,
        is_staff=True,
        is_superuser=True
    )
    print(f"Admin user {username} created successfully!")
    print("You can now login at http://127.0.0.1:8000/")

