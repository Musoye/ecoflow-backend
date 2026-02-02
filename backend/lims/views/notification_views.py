from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Notification
from ..serializers import NotificationSerializer

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def notification_list_create(request):
    
    # --- GET: List ALL Notifications (Everyone sees everything) ---
    if request.method == 'GET':
        # Get all notifications, newest first
        notifications = Notification.objects.all().order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    # --- POST: Broadcast a new message to ALL users ---
    elif request.method == 'POST':
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() # No sender to attach anymore
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def notification_detail(request, pk):
    """ Retrieve or Delete a specific notification by ID """
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'GET':
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        # Simple delete, no sender checks
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)