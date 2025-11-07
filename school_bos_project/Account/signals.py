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

        # 🔒 skip for superusers or staff
        if instance.is_superuser or instance.is_staff:
            return


        if instance.role == "student":
            StudentProfile.objects.create(
                student_name=instance.username,
                email=instance.email,
                enrollement_number=f"ENR{instance.id}"
            )
        elif instance.role == "teacher":
            TeacherProfile.objects.create(user=instance, staff_id=f"TCH{instance.id}", department="General")
        elif instance.role == "parent":
            ParentProfile.objects.create(user=instance, relation="guardian")
        elif instance.role == "staff":
            StaffProfile.objects.create(user=instance, staff_id=f"STF{instance.id}", designation="Staff")