from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Organization, Zone, Camera
from ..serializers import OrganizationSerializer, ZoneSerializer, CameraSerializer

# ==========================================
# ORGANIZATION VIEWS
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def organization_list_create(request):
    
    if request.method == 'GET':
        # Prefetch related zones and cameras for performance
        orgs = Organization.objects.all().prefetch_related('zones__cameras').order_by('-created_at')
        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def organization_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk)

    if request.method == 'GET':
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        org.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# ZONE VIEWS
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def zone_list_create(request):

    if request.method == 'GET':
        # Filter by Organization ID if provided in URL (e.g. ?org_id=1)
        org_id = request.query_params.get('org_id')
        if org_id:
            zones = Zone.objects.filter(organization_id=org_id).select_related('organization').prefetch_related('cameras')
        else:
            zones = Zone.objects.all().select_related('organization').prefetch_related('cameras')
            
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def zone_detail(request, pk):
    zone = get_object_or_404(Zone, pk=pk)

    if request.method == 'GET':
        serializer = ZoneSerializer(zone)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ZoneSerializer(zone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        zone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# CAMERA VIEWS
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def camera_list_create(request):

    if request.method == 'GET':
        # Filter by Zone ID if needed (e.g. ?zone_id=5)
        zone_id = request.query_params.get('zone_id')
        if zone_id:
            cameras = Camera.objects.filter(zone_id=zone_id).select_related('zone__organization')
        else:
            cameras = Camera.objects.all().select_related('zone__organization')

        serializer = CameraSerializer(cameras, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CameraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def camera_detail(request, pk):
    camera = get_object_or_404(Camera, pk=pk)

    if request.method == 'GET':
        serializer = CameraSerializer(camera)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CameraSerializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)