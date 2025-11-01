from django.shortcuts import render
from rest_framework import generics,serializers
from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from schoolApp.models import AdmissionInquiry,Attendance,Notice,FeeModel,FAQ,ClassRoom,Homework,Subject,Class,Book, BookIssue
from Account.models import StaffProfile,TeacherProfile,ParentProfile,StudentProfile
from schoolApp.serializers import AdmissionInquirySerializer,AttendanceSerializer,NoticeSerializer,FeeSerializer,FAQSerializer,SubjectSerializer,ClassRoomSerializer,ClassSerializer,HomeworkSerializer,BookSerializer, BookIssueSerializer
from Account.serializers import StudentProfileSerializer
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework.response import Response
from schoolApp.permissions import IsAdminOrTeacher 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
User =  get_user_model()

@method_decorator(csrf_exempt,name='dispatch')
# class for Subject 
class SubjectAPIView(APIView):
    authentication_classes = []        # Disable SessionAuthentication (CSRF)
    # permission_classes = [AllowAny]
    
    def get(self,request,pk=None):
        if pk:
            subject = Subject.objects.get(pk=pk)
            serializer =SubjectSerializer(subject)
        else:    
            subjects = Subject.objects.all()
            serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    

    def post(self, request):
            serializer = SubjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        subject = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        subject = get_object_or_404(Subject, pk=pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# APIView class for ClassRoom Model
@method_decorator(csrf_exempt,name='dispatch')
class ClassRoomAPIView(APIView):
    # permission_classes = [IsAdminOrTeacher]
    authentication_classes = [] 
    
    def get(self, request):
        classrooms = ClassRoom.objects.all()
        serializer = ClassRoomSerializer(classrooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Admin or Teacher can create (depending on your rule)
        serializer = ClassRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        serializer = ClassRoomSerializer(classroom, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        classroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# APIView for Class Model
@method_decorator(csrf_exempt,name='dispatch')
class ClassAPIView(APIView):
    # permission_classes = [IsAdminUser]
    authentication_classes = [] 

    def get(self, request, pk=None):
        """
        GET all classes or a single class by ID
        """
        if pk:
            school_class = get_object_or_404(Class, pk=pk)
            serializer = ClassSerializer(school_class)
        else:
            classes = Class.objects.all()
            serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new Class
        """
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """
        Update an existing Class
        """
        school_class = get_object_or_404(Class, pk=pk)
        serializer = ClassSerializer(school_class, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Delete a Class
        """
        school_class = get_object_or_404(Class, pk=pk)
        school_class.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdmissionInquiryView(generics.ListCreateAPIView,generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAdminUser]
     
    queryset = AdmissionInquiry.objects.all().order_by('created_at')
    serializer_class = AdmissionInquirySerializer


# Create Student User from Inquiry
# Once the school admin approves an inquiry, convert it into a real student user.
def approve_inquiry(inquiry_id):
    inquiry = AdmissionInquiry.objects.get(id = inquiry_id)

    # create student account
    student_user =User.objects.create_user(
       username = inquiry.student_name,
       email = inquiry.email,
       password = 'default123'
    )

    inquiry.converted = True
    inquiry.save()
    return student_user

class AttendanceView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all().order_by('-date')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Optionally: check if attendance for this student/date already exists
        student = self.request.data.get('student')
        student_name = self.request.data.get('student_name')
        date = serializer.validated_data.get('date')

        if Attendance.objects.filter(student__id=student, date=date).exists():
            raise serializers.ValidationError({"detail": "Attendance already marked for this date."})

        serializer.save()

class NoticeView(generics.ListCreateAPIView):
    queryset = Notice.objects.all().order_by('-date')
    serializer_class = NoticeSerializer        

class FeeView(generics.ListCreateAPIView):
    queryset = FeeModel.objects.all().order_by('due_date')
    serializer_class = FeeSerializer     

    def perform_create(self, serializer):
        instance = serializers.save()
        if instance.due_date<=date.today():
            instance.status='Panding'
            instance.save()

class FAQAutoReplyView(APIView):
    def post(self,request):
        query = request.data.get('query','').lower()
        faq = FAQ.objects.filter(question__icontains=query).first()

        if faq:
            return Response({'answer':faq.answer})
        return Response({'answer':'Sorry, I could`t find that. Please contact schoole admin'})

class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsAuthenticated]


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all().order_by('-created_at')
    serializer_class = HomeworkSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class AdminDashboard(APIView):
    # permission_classes = [IsAdminUser]     

    def get(self,request):
        #Overview counts
        overviews ={
            'total_students':StudentProfile.objects.count(),
            'total_teachers':TeacherProfile.objects.count(),
            'total_staffs':StaffProfile.objects.count(),
            'total_parants':ParentProfile.objects.count(),
            "pending_inquiries": Attendance.objects.count()
        }  
        # Recent admission inquiries (latest 5)
        recent_inquiries = list(
            AdmissionInquiry.objects.order_by('-created_at')[:5].values(
                'id', 'student_name', 'parent_name', 'contact_number', 'email', 'class_name', 'created_at'
            )
        )
         # Teachers list
        teachers_list = list(
            TeacherProfile.objects.select_related('user').values(
                'id', 'user__username', 'subjects'
            )
        )
        # Students list
        students_qs = StudentProfile.objects.select_related('user', 'parent__user')
        students_list = StudentProfileSerializer(students_qs, many=True).data

        # Classes with student count
        classes = []
        for c in Class.objects.all():
            student_count = StudentProfile.objects.filter(class_name=c).count()
            classes.append({
                "id": c.id,
                "class_name": c.class_name,
                "section_name": c.section,
                "student_count": student_count
            })
        # Recent attendance alerts (latest 5 absentees)
        absentees = list(
            Attendance.objects.filter(status='Absent').order_by('-date')[:5].select_related('student').values(
                'id', 'student__username', 'date', 'remark'
            )
        )    
        data = {
            'overviews':overviews,
            'recent_inquiries':recent_inquiries,
            'teachers_list':teachers_list,
            'students_list':students_list,
            'classes':classes,
            'absentees':absentees

        }
        return Response(data)
    
# 📘 Add & List Books
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


# 📕 Issue a Book
class IssueBookView(APIView):
    def post(self, request):
        serializer = BookIssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Book issued successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 📗 Mark Book as Returned
class ReturnBookView(APIView):
    def put(self, request, pk):
        try:
            issue = BookIssue.objects.get(pk=pk)
        except BookIssue.DoesNotExist:
            return Response({"error": "Issue record not found"}, status=404)

        if issue.is_returned:
            return Response({"message": "Book already returned."}, status=400)

        issue.is_returned = True
        issue.save()

        return Response({
            "message": "Book returned successfully",
            "book": issue.book.title,
            "return_date": issue.return_date
        }, status=200)


# 📙 View All Issued Books
class IssuedBookListView(generics.ListAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer    