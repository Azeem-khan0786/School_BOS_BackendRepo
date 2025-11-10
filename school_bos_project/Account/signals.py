# ------------------------------
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import StudentProfile,TeacherProfile,ParentProfile,StaffProfile
from django.contrib.auth import get_user_model
import uuid
from django.db.models import Max

User = get_user_model()
# @receiver(post_save, sender=User)
# def create_related_profiles(sender, instance, created, **kwargs):
    # if created:
    #     # Profile.objects.create(user=instance)

    #     # 🔒 skip for superusers or staff
    #     if instance.is_superuser or instance.is_staff:
    #         return


    #     if instance.role == "student":
    #         StudentProfile.objects.create(
    #             student_name=instance.username,
    #             email=instance.email,
    #             enrollement_number=f"ENR{instance.id}"
    #         )
    #     elif instance.role == "teacher":
    #         TeacherProfile.objects.create(user=instance, staff_id=f"TCH{instance.id}", department="General")
    #     elif instance.role == "parent":
    #         ParentProfile.objects.create(user=instance, relation="guardian")
    #     elif instance.role == "staff":
    #         StaffProfile.objects.create(user=instance, staff_id=f"STF{instance.id}", designation="Staff")

@receiver(pre_save, sender=StudentProfile)
def generate_enrollment_number(sender, instance, **kwargs):
       
    """
    Generate sequential enrollment numbers: ENR000001, ENR000002, etc.
    """
    if not instance.enrollement_no:
        # Get the highest current enrollment number
        max_enrollment = StudentProfile.objects.aggregate(
            max_num=Max('enrollement_no')
        )['max_num']
        
        if max_enrollment and max_enrollment.startswith('ENR'):
            try:
                # Extract number part and increment
                current_num = int(max_enrollment[3:])
                next_num = current_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
        
        # Format as ENR000001, ENR000002, etc.
        instance.enrollement_no = f"ENR{next_num:06d}"            

# Signal to generate sequential staff ID
@receiver(pre_save, sender=TeacherProfile)
def generate_staff_id(sender, instance, **kwargs):
    """
    Generate sequential staff ID: STF1001, STF1002, etc.
    """
    if not instance.staff_id:
        # Get the highest current staff ID
        last_teacher = TeacherProfile.objects.aggregate(
            max_id=Max('staff_id')
        )['max_id']
        
        if last_teacher and last_teacher.startswith('STF'):
            try:
                # Extract number part and increment
                current_num = int(last_teacher[3:])  # Remove 'STF' prefix
                next_num = current_num + 1
            except ValueError:
                # If format is wrong, start from 1001
                next_num = 1001
        else:
            # Start from STF1001
            next_num = 1001
        
        # Format as STF1001, STF1002, etc.
        instance.staff_id = f"STF{next_num}"        