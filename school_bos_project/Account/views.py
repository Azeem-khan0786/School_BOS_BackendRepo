# from django.shortcuts import render
# from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics,status, filters
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
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
        
# @method_decorator(csrf_exempt,name='dispatch')
# class StudentProfileView(APIView):
#     authentication_classes = []        # Disable SessionAuthentication (CSRF)
#     permission_classes = [AllowAny]     # Allow public access for now
#     def get(self, request, pk):
#         try:
#             profile = StudentProfile.objects.get(pk=pk)
#             serializer = StudentProfileSerializer(profile)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except StudentProfile.DoesNotExist:
#             return Response(
#                 {"error": "Profile not found"},   # no serializer here
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#     def put(self,request,pk):
#         try:
#             profile = StudentProfile.objects.get(pk=pk)
#             serializer = StudentProfileSerializer(profile,data = request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data,status=status.HTTP_200_OK)
#         except StudentProfile.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
        
#     def delete(self,request,pk):
#         profile = StudentProfile.objects.get(pk=pk)
#         profile.delete()
#         return Response("Student Profile Deleted")
    

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all().select_related('class_name')
    serializer_class = StudentProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student_name', 'email', 'enrollement_no', 'parent_name']
    filterset_fields = ['class_name', 'section_name', 'gender', 'is_active']
    ordering_fields = ['student_name', 'admission_date', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        # Enrollment number will be auto-generated by signal
        serializer.save()

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentProfile.objects.all().select_related('class_name')
    serializer_class = StudentProfileSerializer

    def perform_update(self, serializer):
        # Prevent updating read-only fields
        if 'enrollement_no' in serializer.validated_data:
            del serializer.validated_data['enrollement_no']
        if 'created_at' in serializer.validated_data:
            del serializer.validated_data['created_at']
        serializer.save()


class StudentSearchView(generics.ListAPIView):
    serializer_class = StudentProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['student_name', 'email', 'enrollement_no']

    def get_queryset(self):
        queryset = StudentProfile.objects.all().select_related('class_name')
        
        # Additional filtering by class if provided
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_name_id=class_id)
            
        return queryset
    
class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = TeacherProfile.objects.all().prefetch_related('subjects')
    serializer_class = TeacherProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['teacher_name', 'email', 'staff_id', 'department', 'specialization', 'aadhaar_number']
    filterset_fields = ['department', 'gender', 'is_active', 'specialization']
    ordering_fields = ['teacher_name', 'joining_date', 'experience', 'created_at']
    ordering = ['-created_at']

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherProfile.objects.all().prefetch_related('subjects')
    serializer_class = TeacherProfileSerializer

    def perform_update(self, serializer):
        # Prevent updating read-only fields
        read_only_fields = ['staff_id', 'created_at', 'updated_at']
        for field in read_only_fields:
            if field in serializer.validated_data:
                del serializer.validated_data[field]
        serializer.save()

class TeacherSearchView(generics.ListAPIView):
    serializer_class = TeacherProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['teacher_name', 'email', 'staff_id', 'department', 'specialization']

    def get_queryset(self):
        queryset = TeacherProfile.objects.all().prefetch_related('subjects')
        
        # Additional filtering by department if provided
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
            
        return queryset


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