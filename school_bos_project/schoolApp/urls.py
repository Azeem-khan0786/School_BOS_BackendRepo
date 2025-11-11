
from django.urls import path
from schoolApp import views 
from rest_framework.routers import DefaultRouter
from .views import HomeworkViewSet, ClassRoomViewSet,SubjectAPIView,ClassRoomAPIView,ClassAPIView

router = DefaultRouter()
router.register(r'classrooms', ClassRoomViewSet)
router.register(r'homeworks', HomeworkViewSet)

urlpatterns = [
    path('admission_inquiries/', views.AdmissionInquiryView.as_view(), name='admission-inquiry-list-create'),
    path('admission_inquiries/<int:pk>/', views.AdmissionInquiryView.as_view(), name='admission-inquiry-detail'),
    
    path('subjects/', SubjectAPIView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', SubjectAPIView.as_view(), name='subject-detail'),

    path('classrooms/', ClassRoomAPIView.as_view(), name='classroom-list'),
    path('classrooms/<int:pk>/', ClassRoomAPIView.as_view(), name='classroom-detail'), 

    # GET /attendance/class/1/students/
    path('class/<int:class_id>/students/', views.ClassStudentsView.as_view(), name='class-students'),
    path('mark/', views.MarkAttendanceView.as_view(), name='mark-attendance'),

    # Class APIs
    path('classes/', ClassAPIView.as_view(), name='class-list'),
    path('classes/<int:pk>/', ClassAPIView.as_view(), name='class-detail'),

    # path('attendence', views.AttendanceView.as_view(), name='attendance'),
    path('approve_inquiry', views.approve_inquiry, name='approve_inquiry'),
    path('notice', views.NoticeView.as_view(), name='notice'),
    path('fee', views.FeeView.as_view(), name='fee'),
    path('faq', views.FAQAutoReplyView.as_view(), name='faq-auto-reply'),
    path('admin_dashboard', views.AdminDashboard.as_view(), name='admin_dashboard'),
  
    # Library management
    path('books/', views.BookListCreateView.as_view(), name='book-list-create'),     # GET, POST
    path('issue/', views.IssueBookView.as_view(), name='issue-book'),                # POST
    path('return/<int:pk>/', views.ReturnBookView.as_view(), name='return-book'),    # PUT
    path('issued/', views.IssuedBookListView.as_view(), name='issued-books'),        # GET

    # TimeTable
    path('timetables/', views.TimeTableListAPIView.as_view(), name='timetable-list'),
    path('timetables/create/', views.TimeTableCreateAPIView.as_view(), name='timetable-create'),
    path('timetables/<int:pk>/', views.TimeTableDetailAPIView.as_view(), name='timetable-detail'),
    path('timetables/<int:pk>/update/',views.TimeTableUpdateAPIView.as_view(), name='timetable-update'),
    path('timetables/<int:pk>/delete/', views.TimeTableDeleteAPIView.as_view(), name='timetable-delete'),
]

# ✅ Combine with router URLs
urlpatterns += router.urls