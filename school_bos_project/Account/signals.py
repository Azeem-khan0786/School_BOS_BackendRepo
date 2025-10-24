# ------------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentProfile,TeacherProfile,ParentProfile,StaffProfile
from django.contrib.auth import get_user_model

User = get_user_model()
@receiver(post_save, sender=User)
def create_related_profiles(sender, instance, created, **kwargs):
    if created:
        # Profile.objects.create(user=instance)

        if instance.role == "student":
            StudentProfile.objects.create(user=instance, admission_number=f"ADM{instance.id}")
        elif instance.role == "teacher":
            TeacherProfile.objects.create(user=instance, staff_id=f"TCH{instance.id}", department="General")
        elif instance.role == "parent":
            ParentProfile.objects.create(user=instance, relation="guardian")
        elif instance.role == "staff":
            StaffProfile.objects.create(user=instance, staff_id=f"STF{instance.id}", designation="Staff")