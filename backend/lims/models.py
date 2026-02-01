from django.db import models

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