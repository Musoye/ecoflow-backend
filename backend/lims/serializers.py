from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Organization, Zone, Camera, Alert, Notification

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        # We must use create_user to hash the password correctly
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.USER)
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """ Used for retrieving and updating user info """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'eco_points', 'full_name']
        read_only_fields = ['email', 'role', 'eco_points'] # Prevent users from changing their own role/points

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom JWT Login to include user info in the response """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra data to the response (optional but helpful for frontend)
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['name'] = self.user.first_name
        return data
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
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'heading', 'sub_heading', 'status', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at']
        read_only_fields = ['created_at']