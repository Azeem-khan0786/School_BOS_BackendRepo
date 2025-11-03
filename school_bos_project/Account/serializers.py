from rest_framework import serializers
from django.contrib.auth import authenticate,get_user_model

from Account.models import User ,StudentProfile,TeacherProfile,StaffProfile,ParentProfile
User  =  get_user_model()
# ---------------------------
# Registration Serializer
# ---------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'confirm_password', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # remove confirm password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student')
        )
        return user
    
# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        data["user"] = user
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        # Check new passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Optionally add password strength validation
        if len(new_password) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user    
class TeacherProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TeacherProfile
        fields = "__all__"

class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = StaffProfile
        fields = "__all__"
class ParentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ParentProfile
        fields = "__all__"
class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    # profile = ProfileSerializer(source='user.profile', read_only=True)  # show related profile
    parent = ParentProfileSerializer(read_only=True)  

    class Meta:
        model = StudentProfile
        fields = "__all__"        


    def validate_user(self, value):
        # Check if the user's role is student
        if value.role != 'student':
            raise serializers.ValidationError("The selected user must have the role 'student'.")
        return value
