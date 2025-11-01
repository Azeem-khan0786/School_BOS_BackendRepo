from django.contrib import admin

# Register your models here.
from schoolApp.models import AdmissionInquiry,Attendance,Subject, ClassRoom, Class,Homework,Subject,FeeModel,FAQ,Book,BookIssue


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'code', 'created_at')
    search_fields = ('subject', 'code')
    ordering = ('subject',)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_room', 'capacity', 'location')
    search_fields = ('name', 'location')
    list_filter = ('location',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'section', 'student_count', 'max_seats')
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

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'isbn', 'category', 'quantity', 'available_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)
    ordering = ('title',)


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'book', 'issued_to', 'issue_date', 'due_date',
        'return_date', 'is_returned'
    )
    list_filter = ('is_returned', 'issue_date', 'due_date')
    search_fields = ('book__title', 'issued_to__username')
    ordering = ('-issue_date',)



