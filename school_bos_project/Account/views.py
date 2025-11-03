# from django.shortcuts import render
# from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer,ChangePasswordSerializer,StudentProfileSerializer,TeacherProfileSerializer,StaffProfileSerializer,ParentProfileSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from .models import User,StudentProfile,TeacherProfile,StaffProfile,ParentProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login , logout

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = RegisterSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# Login API
# ---------------------------

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "username": user.username,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
# logged out 
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        
@method_decorator(csrf_exempt,name='dispatch')
class StudentProfileView(APIView):
    authentication_classes = []        # Disable SessionAuthentication (CSRF)
    permission_classes = [AllowAny]     # Allow public access for now
    def get(self, request, pk):
        try:
            profile = StudentProfile.objects.get(pk=pk)
            serializer = StudentProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},   # no serializer here
                status=status.HTTP_404_NOT_FOUND
            )
        
    def put(self,request,pk):
        try:
            profile = StudentProfile.objects.get(pk=pk)
            serializer = StudentProfileSerializer(profile,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def delete(self,request,pk):
        profile = StudentProfile.objects.get(pk=pk)
        profile.delete()
        return Response("Student Profile Deleted")
    
@method_decorator(csrf_exempt,name='dispatch')
class ParentProfileView(APIView):
    authentication_classes = []        # Disable SessionAuthentication (CSRF)
    permission_classes = [AllowAny]     # Allow public access for now
    def get(self, request, pk):
        try:
            profile = ParentProfile.objects.get(pk=pk)
            serializer = ParentProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ParentProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},   # no serializer here
                status=status.HTTP_404_NOT_FOUND
            )
   
    def put(self,request,pk):
        try:
            profile = ParentProfile.objects.get(pk=pk)
            serializer = ParentProfileSerializer(profile,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
        except ParentProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)        
    
    def delete(self,request,pk):
            profile = ParentProfile.objects.get(pk=pk)
            profile.delete()
            return Response("Parent Profile Deleted")

@method_decorator(csrf_exempt, name='dispatch')
class TeacherProfileView(APIView):
    authentication_classes = []        # Disable SessionAuthentication (CSRF)
    permission_classes = [AllowAny]     # Allow public access for now

    def get(self, request, pk):
        try:
            profile = TeacherProfile.objects.get(pk=pk)
            serializer = TeacherProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            profile = TeacherProfile.objects.get(pk=pk)
            serializer = TeacherProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
@method_decorator(csrf_exempt, name='dispatch')

            
class StaffProfileView(APIView):
    authentication_classes = []        # Disable SessionAuthentication (CSRF)
    permission_classes = [AllowAny]    # Allow public access for now
    def get(self, request, pk):
        try:
            profile = StaffProfile.objects.get(pk=pk)
            serializer = StaffProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StaffProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},   # no serializer here
                status=status.HTTP_404_NOT_FOUND
            )
   
    def put(self,request,pk):
        try:
            profile = StaffProfile.objects.get(pk=pk)
            serializer = StaffProfileSerializer(profile,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
        except StaffProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)        

    def delete(self,request,pk):
            profile = StaffProfile.objects.get(pk=pk)
            profile.delete()
            return Response("StaffProfile  Deleted") 