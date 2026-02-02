from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from django.conf import settings

class User(AbstractUser):
    # Define the 4 Roles
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "admin"
        USER = "USER", "user"

    base_role = Role.USER

    email = models.EmailField(unique=True)
    
    # The new Role Field
    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    eco_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Organization(models.Model):
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=100)  # e.g., 'Corporate', 'Warehouse'
    total_capacity = models.PositiveIntegerField(default=0)
    
    # Geo-location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Zone(models.Model):
    # Link to Parent Organization
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='zones')
    
    name = models.CharField(max_length=255)
    zone_type = models.CharField(max_length=100) # e.g., 'Room', 'Hall'
    capacity = models.PositiveIntegerField(default=0)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

class Camera(models.Model):
    # Link to Parent Zone
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='cameras')
    
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.zone.name})"

class Alert(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'

    heading = models.CharField(max_length=255)
    sub_heading = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.heading} ({self.status})"
class Notification(models.Model):
    # ID is automatically added by Django (id field)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Automatically set the time when created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (ID: {self.id})"

class CarbonLog(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='carbon_logs')
    saved_amount = models.FloatField(help_text="Amount of Carbon saved (kg/g)")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone.name} - {self.saved_amount} saved"