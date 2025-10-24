from django.db import models
from django.conf import settings
from django.utils import timezone
from multiselectfield import MultiSelectField

    # Admission inquiry form (student + parent details)
    # AdmissionInquiry form for new user who doen`t have accout in database
class Subject(models.Model):
    subject = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)  # e.g., MATH101
    description = models.TextField(blank=True, null=True)  # brief info about the subject
    # grade_level = models.CharField(max_length=50, blank=True, null=True)  # e.g., Class 5, Class 6
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject']

    def __str__(self):
        return f"{self.subject} ({self.code})" if self.code else self.subject
    
class ClassRoom(models.Model):
    BOARD_CHOICES = [
        ('blackboard', 'Blackboard'),
        ('whiteboard', 'Whiteboard'),
        ('projector', 'Projector'),
        ('smart_board', 'Smart Board'),
        ('digital_display', 'Digital Display'),
    ]
    name = models.CharField(max_length=50)
    # section_name = models.CharField(max_length=10, blank=True, null=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    facilities  = MultiSelectField(
        max_length=225,
        choices=BOARD_CHOICES,
        default='blackboard',
        help_text="Type of board or teaching equipment available"
    )
    def __str__(self):
        return f"{self.name}" 
    
class Class(models.Model):
    """Represents an academic class such as 'Class X - A'."""
    name = models.CharField(max_length=50)               # e.g., Class X
    section = models.CharField(max_length=10, blank=True, null=True)  # e.g., A, B
    subjects = models.ManyToManyField(Subject, related_name='classes')
    classrooms = models.ManyToManyField(ClassRoom, related_name='classes')
    student_count = models.PositiveIntegerField(default=0)
    max_seats = models.PositiveIntegerField(default=40)

    def __str__(self):
        return f"{self.name} {self.section or ''}".strip()
    
class AdmissionInquiry(models.Model):
    student_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    class_name = models.CharField(max_length=50)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.class_name}"
    #    Attendance alerts to parents    
class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.date} ({self.status})"  
      
# Basic notices ( Time table ,holidays, PTM, events)    
class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    audience_type = MultiSelectField(max_length=50, choices=[
        ('All', 'All'),
        ('Parents', 'Parents'),
        ('Students', 'Students'),
        ('Teachers', 'Teachers')
    ])
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title    

# Fee due reminders
class FeeModel(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)   
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    due_date = models.DateField()
    status = models.CharField( max_length=10,choices=[('Paid','Paid'),('Panding','Panding')],default='Panding')
    
    def __str__(self):
        return f"{self.student.username}-{self.status}"

class FAQ(models.Model):
    questions  = models.CharField(max_length=255)
    answer  = models.TextField()

    def __str__(self):
        return f"{self.questions}"
    
# Homework & assignment sharing
class Homework(models.Model):
    ASSIGNMENT_TYPE_CHOICES = [
        ('class', 'Whole Class'),
        ('student', 'Specific Student(s)'),
    ]

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='homeworks')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='homeworks', blank=True, null=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_homeworks', blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    due_date = models.DateField()
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    assignment_type = models.CharField(max_length=10, choices=ASSIGNMENT_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.get_assignment_type_display()})"
