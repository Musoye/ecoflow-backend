from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.db.utils import OperationalError
from ..permissions import IsAdmin, IsAnalyst, IsDirector, IsManager


@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request):
    """ A simple status check endpoint """
    return Response({"status": "OK", "message": "Ecoflow system is operational."}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])
def system_health(request):
    """ A more detailed health check endpoint """
    
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "OK"
    except OperationalError:
        db_status = "DOWN"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    external_service_status = "OK" 

    if db_status == "OK" and external_service_status == "OK":
        overall_status = "OK"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "DEGRADED"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response({
        "overall_status": overall_status,
        "database": db_status,
        "external_service": external_service_status
    }, status=http_status)