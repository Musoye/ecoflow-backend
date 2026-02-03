from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Alert
from ..serializers import AlertSerializer

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Or AllowAny, depending on your needs
def alert_list_create(request):
    
    # --- GET: List all alerts ---
    if request.method == 'GET':
        # Optional: Filter by status (e.g., /api/alerts/?status=OPEN)
        status_param = request.query_params.get('status')
        
        if status_param:
            alerts = Alert.objects.filter(status=status_param).order_by('-created_at')
        else:
            alerts = Alert.objects.all().order_by('-created_at')
            
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    # --- POST: Create a new alert ---
    elif request.method == 'POST':
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def alert_detail(request, pk):
    alert = get_object_or_404(Alert, pk=pk)

    # --- GET: Retrieve single alert ---
    if request.method == 'GET':
        serializer = AlertSerializer(alert)
        return Response(serializer.data)

    # --- PUT: Update alert (e.g., Close it) ---
    elif request.method == 'PUT':
        serializer = AlertSerializer(alert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE: Remove alert ---
    elif request.method == 'DELETE':
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)