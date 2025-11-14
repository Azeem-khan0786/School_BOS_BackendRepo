from django.contrib import admin
from chat.models import ChatState


@admin.register(ChatState)
class ChatStateAdmin(admin.ModelAdmin):
    list_display = ("phone", "current_menu", "selected_student_id", "updated_at")
    search_fields = ("phone", "current_menu")
    list_filter = ("current_menu", "updated_at")
    ordering = ("-updated_at",)
