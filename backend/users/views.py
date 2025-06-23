from users.serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"New user registered: {user.username} ({user.role})")
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            logger.warning("User registration failed", extra={'errors': serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}", exc_info=True)
            return Response({'error': 'An error occurred during registration'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AccessOnlyTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {'access': data['access']}

class LoginView(TokenObtainPairView):
    try:
        serializer_class = AccessOnlyTokenSerializer
    except Exception as e:
        logger.error(f"Error setting serializer class for LoginView: {str(e)}", exc_info=True)
        raise e

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}", exc_info=True)
            return Response({'error': 'An error occurred while retrieving the profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)