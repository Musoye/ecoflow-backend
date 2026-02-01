from rest_framework import serializers
from .models import Organization, Zone, Camera

# --- 1. Simple Serializers (For embedding inside other objects) ---

class SimpleOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_type']

class SimpleCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'name', 'is_active']

class SimpleZoneSerializer(serializers.ModelSerializer):
    # Embed the organization details so we know where this zone belongs
    organization = SimpleOrganizationSerializer(read_only=True)
    
    class Meta:
        model = Zone
        fields = ['id', 'name', 'zone_type', 'organization']

# --- 2. Main Serializers (For the Views) ---

class CameraSerializer(serializers.ModelSerializer):
    """
    Shows the Camera, plus its Zone (Parent) and Organization (Grandparent)
    """
    zone = SimpleZoneSerializer(read_only=True)  # Read-only nested data
    zone_id = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(), source='zone', write_only=True
    ) # For creating/updating

    class Meta:
        model = Camera
        fields = ['id', 'name', 'is_active', 'zone', 'zone_id', 'created_at']


class ZoneSerializer(serializers.ModelSerializer):
    """
    Shows the Zone, its Organization (Parent), AND its Cameras (Children)
    """
    organization = SimpleOrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True
    )
    
    # Retrieve all cameras in this zone
    cameras = SimpleCameraSerializer(many=True, read_only=True)

    class Meta:
        model = Zone
        fields = ['id', 'name', 'zone_type', 'capacity', 'latitude', 'longitude', 
                  'organization', 'organization_id', 'cameras']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Shows the Organization, and deeply nested Zones -> Cameras
    """
    # Custom serializer inside to fetch zones WITH their cameras
    class ZoneWithCamerasSerializer(serializers.ModelSerializer):
        cameras = SimpleCameraSerializer(many=True, read_only=True)
        class Meta:
            model = Zone
            fields = ['id', 'name', 'zone_type', 'cameras']

    zones = ZoneWithCamerasSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_type', 'total_capacity', 'latitude', 'longitude', 'zones']