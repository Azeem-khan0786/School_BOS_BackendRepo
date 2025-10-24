from django.contrib import admin

# Register your models here.
from schoolApp.models import AdmissionInquiry,Attendance,Subject, ClassRoom, Class,Homework,Subject,FeeModel,FAQ


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'code', 'created_at')
    search_fields = ('subject', 'code')
    ordering = ('subject',)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'capacity', 'location')
    search_fields = ('name', 'location')
    list_filter = ('location',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'section', 'student_count', 'max_seats')
    list_filter = ('section',)
    search_fields = ('name',)
    filter_horizontal = ('subjects', 'classrooms')  # Nice UI for M2M fields

    # ✅ Extra validation in admin (same as serializer)
    def save_model(self, request, obj, form, change):
        if obj.student_count > obj.max_seats:
            raise ValueError("Student count cannot exceed maximum seats.")
        super().save_model(request, obj, form, change)


admin.site.register(AdmissionInquiry)
admin.site.register(Attendance)
admin.site.register(Homework)
admin.site.register(FeeModel)
admin.site.register(FAQ)





