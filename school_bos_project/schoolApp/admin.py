from django.contrib import admin

# Register your models here.
from schoolApp.models import AdmissionInquiry,Attendance,Subject, ClassRoom, Class,Homework,Subject,FeeModel,FAQ,Book,BookIssue,Exam,ExamSubject,ReportCard,Grade,TimeTable,NoticeModel
from Account.models import StudentProfile

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
    filter_horizontal = ('subjects',)  # Nice UI for M2M fields

    # ✅ Extra validation in admin (same as serializer)
    def save_model(self, request, obj, form, change):
        if obj.student_count > obj.max_seats:
            raise ValueError("Student count cannot exceed maximum seats.")
        super().save_model(request, obj, form, change)


admin.site.register(AdmissionInquiry)
admin.site.register(Attendance)
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


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'exam_type', 
        'class_name', 
        'academic_year', 
        'exam_date', 
        'status',
        'is_upcoming_display'
    ]
    list_filter = ['exam_type', 'class_name', 'academic_year', 'status']
    search_fields = ['name', 'class_name__name']
    list_per_page = 20
    # inlines = [ExamSubjectInline]
    
    def is_upcoming_display(self, obj):
        return obj.is_upcoming
    is_upcoming_display.boolean = True
    is_upcoming_display.short_description = 'Upcoming'

@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ['exam', 'subject', 'max_marks', 'exam_time']
    list_filter = ['exam__class_name', 'subject']
    search_fields = ['exam__name', 'subject__subject']
    list_per_page = 20

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'exam', 
        'subject', 
        'marks_obtained', 
        'max_marks', 
        'percentage',
        'grade',
        'created_at'
    ]
    list_filter = ['exam__class_name', 'subject', 'grade']
    search_fields = ['student__name', 'exam__name', 'subject__subject']
    list_per_page = 25
    readonly_fields = ['percentage', 'grade', 'remarks']

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'exam',
        'obtained_marks',
        'total_marks',
        'overall_percentage',
        'overall_grade',
        'rank',
        'created_at'
    ]
    list_filter = ['exam__class_name', 'exam__academic_year']
    search_fields = ['student__name', 'exam__name']
    list_per_page = 20
    readonly_fields = ['overall_percentage', 'overall_grade']


@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file_type', 'uploaded_by', 'uploaded_on')
    list_filter = ('file_type', 'uploaded_by', 'uploaded_on')
    search_fields = ('title', 'description', 'file')
    readonly_fields = ('file_type', 'uploaded_on')  #uploaded_by
    ordering = ('-uploaded_on',)


    # def save_model(self, request, obj, form, change):
    #     # Automatically set uploaded_by if not manually set
    #     if not obj.uploaded_by:
    #         obj.uploaded_by = request.user
    #     super().save_model(request, obj, form, change)


@admin.register(NoticeModel)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'target', 'class_name', 'applicable_date', 'posted_by', 'is_published', 'created_at']
    list_filter = ['target', 'class_name', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'specific_students']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('title', 'description', 'applicable_date')
#         }),
#         ('Targeting', {
#             'fields': ('target', 'class_name', 'specific_students')
#         }),
#         ('Publication', {
#             'fields': ('posted_by', 'is_published')
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )    
@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_name']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "students":
            class_id = request.GET.get('class_name')  # Works when class is selected first
            if class_id:
                kwargs["queryset"] = StudentProfile.objects.filter(class_name_id=class_id)
            else:
                kwargs["queryset"] = StudentProfile.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)