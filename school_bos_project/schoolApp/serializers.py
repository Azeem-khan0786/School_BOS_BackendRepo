from rest_framework import serializers
from django.contrib.auth import authenticate,get_user_model

# from Account.models import User, Profile ,StudentProfile,TeacherProfile,StaffProfile,ParentProfile

from schoolApp.models import AdmissionInquiry,Attendance,Notice,FeeModel,FAQ,ClassRoom,Homework, Subject,Class,Book, BookIssue, Exam, ExamSubject, Grade, ReportCard
User  =  get_user_model()


# serializer for AdmissionInquiry 
class AdmissionInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionInquiry
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(write_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'status', 'date']
        extra_kwargs = {'student': {'read_only': True}}

    def create(self, validated_data):
        student_name = validated_data.pop('student_name')
        User = get_user_model()
        student = User.objects.filter(username__iexact=student_name).first()

        if not student:
            raise serializers.ValidationError({"student_name": "Student not found"})
        
        attendance = Attendance.objects.create(student=student, **validated_data)
        return attendance
    
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Subject.objects.all()
    )
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ClassRoom.objects.all()
    )

    class Meta:
        model = Class
        fields = '__all__'

    def validate(self, data):
        # ✅ Ensure class has not more than 7 subjects
        subjects = data.get('subjects', [])
        # ✅ Ensure student_count <= max_seats
        student_count = data.get('student_count')
        max_seats = data.get('max_seats')

        if student_count is not None and max_seats is not None:
            if student_count > max_seats:
                raise serializers.ValidationError(
                    "Student count cannot be greater than maximum seats available."
                )

        return data
        
class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
class FeeSerializer(serializers.ModelSerializer):
    class Meta:
         model = FeeModel   
         fields = '__all__'    
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
         model = FAQ   
         fields = '__all__'          



class HomeworkSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    classroom_name = serializers.CharField(source='classroom.__str__', read_only=True)
    student_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='students',
        many=True,
        required=False
    )
    student_names = serializers.SlugRelatedField(
        slug_field='username', source='students', read_only=True, many=True
    )

    class Meta:
        model = Homework
        fields = [
            'id', 'teacher', 'teacher_name',
            'assignment_type',  'classroom_name',
            'student_ids', 'student_names',
            'title', 'description', 'subject', 'due_date', 'file', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        assignment_type = attrs.get('assignment_type')
        classroom = attrs.get('classroom')
        students = attrs.get('students', [])

        if assignment_type == 'class' and not classroom:
            raise serializers.ValidationError({"classroom": "Classroom is required for class assignments."})
        if assignment_type == 'student' and not students:
            raise serializers.ValidationError({"students": "At least one student is required for student-specific assignments."})

        return attrs

    def create(self, validated_data):
        students = validated_data.pop('students', [])
        homework = Homework.objects.create(**validated_data)
        if students:
            homework.students.set(students)
        return homework        

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookIssueSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    issued_user = serializers.CharField(source='issued_to.username', read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            'id', 'book', 'book_title', 'issued_to', 'issued_user',
            'issue_date', 'due_date', 'return_date', 'is_returned'
        ]    
    def validate(self, data):
        issue_date = data.get("issue_date")
        due_date = data.get("due_date")
        return_date = data.get("return_date")
        is_returned = data.get("is_returned", False)

        if due_date and issue_date and due_date < issue_date:
            raise serializers.ValidationError("Due date must be after issue date.")
        if return_date and issue_date and return_date < issue_date:
            raise serializers.ValidationError("Return date cannot be before issue date.")
        if is_returned and not return_date:
            raise serializers.ValidationError("Return date required when returned is True.")

        return data


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.subject', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    
    class Meta:
        model = ExamSubject
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class_name_detail = ClassSerializer(source='class_name', read_only=True)
    subjects = ExamSubjectSerializer(source='exam_subjects', many=True, read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    upcoming_subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = '__all__'
    
    def get_upcoming_subjects(self, obj):
        """Get subjects for this exam that haven't been graded for a student"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # You can customize this based on your needs
            # For example, get subjects that student hasn't taken yet
            return ExamSubjectSerializer(
                obj.exam_subjects.all(), 
                many=True
            ).data
        return []

class ExamCreateSerializer(serializers.ModelSerializer):
    subjects = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="List of subjects with max_marks: [{'subject': 1, 'max_marks': 100}]"
    )
    
    class Meta:
        model = Exam
        fields = '__all__'
    
    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        exam = Exam.objects.create(**validated_data)
        
        # Create exam subjects
        for subject_data in subjects_data:
            ExamSubject.objects.create(
                exam=exam,
                subject_id=subject_data['subject'],
                max_marks=subject_data['max_marks']
            )
        
        return exam

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    class_name = serializers.CharField(source='exam.class_name.name', read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ('grade', 'percentage', 'remarks')

class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    exam_details = ExamSerializer(source='exam', read_only=True)
    grades = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportCard
        fields = '__all__'
    
    def get_grades(self, obj):
        grades = Grade.objects.filter(student=obj.student, exam=obj.exam)
        return GradeSerializer(grades, many=True).data