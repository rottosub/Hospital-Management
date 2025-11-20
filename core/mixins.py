from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is an approved Admin"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()


class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is an approved Doctor"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_doctor()


class PatientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is an approved Patient"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_patient()


class RoleBasedAccessMixin(LoginRequiredMixin):
    """Mixin that allows access based on role"""
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.role not in self.allowed_roles or not request.user.is_approved:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return super().dispatch(request, *args, **kwargs)

