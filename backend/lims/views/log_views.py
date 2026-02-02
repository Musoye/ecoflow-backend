from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers import MyTokenObtainPairSerializer

# Create a custom view that uses the serializer we created in Step 2
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer