from django.shortcuts import render
from rest_framework import generics,serializers
from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny,SAFE_METHODS,BasePermission
from schoolApp.models import AdmissionInquiry,Attendance,FeeModel,FAQ,ClassRoom,Homework,Subject,Class,Book, BookIssue,TimeTable
from Account.models import StaffProfile,TeacherProfile,ParentProfile,StudentProfile
from schoolApp.serializers import AdmissionInquirySerializer,AttendanceSerializer,FeeSerializer,FAQSerializer,SubjectSerializer,ClassRoomSerializer,ClassSerializer,HomeworkSerializer,BookSerializer, BookIssueSerializer,TimeTableSerializer
from Account.serializers import StudentProfileSerializer
from django.contrib.auth import get_user_model
from datetime import date,timezone
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

# Get all students of a class
class ClassStudentsView(APIView):
    def get(self, request, class_id):
        students = StudentProfile.objects.filter(class_room_id=class_id)
        data = [
            {"id": s.id, "name": s.user.username, "enrollment_no": s.enrollment_no}
            for s in students
        ]
        return Response(data)


# Mark attendance for all students in class
class MarkAttendanceView(APIView):
    def post(self, request):
        class_room_id = request.data.get('class_room')
        records = request.data.get('records', [])
        date = timezone.now().date()

        responses = []
        for record in records:
            student_id = record.get('student')
            status_value = record.get('status')

            attendance, created = Attendance.objects.update_or_create(
                student_id=student_id,
                date=date,
                defaults={'class_room_id': class_room_id, 'status': status_value}
            )
            responses.append(AttendanceSerializer(attendance).data)

        return Response({"message": "Attendance marked successfully", "data": responses}, status=status.HTTP_201_CREATED)

# class NoticeView(generics.ListCreateAPIView):
    # queryset = Notice.objects.all().order_by('-created_at')
    # serializer_class = NoticeSerializer     
    pass   

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
        serializer.save(Assigned_By_teacher=self.request.user)

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
            "return_date": issue.return_date,
            'issue_date' : issue.issue_date,
            'due_date' : issue.due_date,
    
        }, status=200)


# 📙 View All Issued Books
class IssuedBookListView(generics.ListAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer    


class IsAdminUserOrReadOnly(BasePermission):
    """
    Allow only admin users to create, update, or delete.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# 🔹 CREATE (Upload TimeTable)
class TimeTableCreateAPIView(APIView):
    # permission_classes = [IsAdminUserOrReadOnly]

    def post(self, request):
        serializer = TimeTableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 LIST (Get All TimeTables - Upload History)
class TimeTableListAPIView(APIView):
    permission_classes = [AllowAny]  # everyone can view

    def get(self, request):
        timetables = TimeTable.objects.all().order_by('-uploaded_on')
        serializer = TimeTableSerializer(timetables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 RETRIEVE (Get Single TimeTable by ID)
class TimeTableDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            timetable = TimeTable.objects.get(pk=pk)
        except TimeTable.DoesNotExist:
            return Response({'error': 'TimeTable not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TimeTableSerializer(timetable)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 UPDATE (Full update)
class TimeTableUpdateAPIView(APIView):
    # permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, pk):
        try:
            timetable = TimeTable.objects.get(pk=pk)
        except TimeTable.DoesNotExist:
            return Response({'error': 'TimeTable not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TimeTableSerializer(timetable, data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 DELETE (Remove TimeTable)
class TimeTableDeleteAPIView(APIView):
    # permission_classes = [IsAdminUserOrReadOnly]

    def delete(self, request, pk):
        try:
            timetable = TimeTable.objects.get(pk=pk)
        except TimeTable.DoesNotExist:
            return Response({'error': 'TimeTable not found'}, status=status.HTTP_404_NOT_FOUND)

        timetable.delete()
        return Response({'message': 'TimeTable deleted successfully'}, status=status.HTTP_204_NO_CONTENT)   