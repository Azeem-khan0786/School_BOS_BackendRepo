from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from schoolApp.models import  Subject
# -------------------
# Custom User Model
# -------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    # ---- Moved from Profile ----
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    language_preference = models.CharField(max_length=50, default="English")

    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

# -------------------
# Common Profile
# -------------------
# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     gender = models.CharField(max_length=10, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
#     language_preference = models.CharField(max_length=50, default="English")

#     def __str__(self):
#         return f"Profile of {self.user.username}"


# -------------------
# Student Profile
# -------------------
class StudentProfile(models.Model):
    
     # ---- Basic user-related fields ----
    student_name = models.CharField(max_length=150, unique=True,default='xyz')
    email = models.EmailField(unique=True,default='xyz@gail.com')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    language_preference = models.CharField(max_length=50, default="English")

    # ---- Student-specific fields ----
    enrollement_number = models.CharField(max_length=20, unique=True, editable=False,blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    class_name = models.OneToOneField("schoolApp.Class",  on_delete=models.CASCADE)
    section_name = models.CharField(max_length=10)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_contact = models.CharField(max_length=15, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Student {self.student_name} - {self.class_name}{self.section_name}"


# -------------------
# Teacher Profile
# -------------------
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    joining_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Teacher {self.user.username}"


# -------------------
# Parent Profile
# -------------------
class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parent_profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    relation = models.CharField(
        max_length=20,
        choices=(("father", "Father"), ("mother", "Mother"), ("guardian", "Guardian"))
    )
    occupation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Parent {self.user.username}"


# -------------------
# Staff Profile
# -------------------
class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
    staff_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Staff {self.user.username} - {self.designation}"
    
