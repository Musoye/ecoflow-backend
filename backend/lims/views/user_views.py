from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    MyTokenObtainPairSerializer
)

# --- 1. REGISTRATION ---
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "user": {
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 2. LOGIN (Custom JWT) ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- 3. GET & UPDATE CURRENT USER ---
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user

    # GET: Retrieve current user details
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # PUT/PATCH: Update current user details
    elif request.method in ['PUT', 'PATCH']:
        # partial=True allows updating just 'first_name' without sending everything
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)