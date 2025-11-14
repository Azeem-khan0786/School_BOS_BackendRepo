# in models.py
from django.db import models

class ChatState(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    current_menu = models.CharField(max_length=100, default="main_menu")
    selected_student_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone} → {self.current_menu} ({self.selected_student_id})"
