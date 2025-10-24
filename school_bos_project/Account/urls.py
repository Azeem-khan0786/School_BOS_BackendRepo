

from django.urls import path
from Account import views  

urlpatterns = [
    
    path('register/', views.RegisterView.as_view(), name='register'),       # POST
    path('register/<int:pk>/', views.RegisterView.as_view(), name='user-detail'),  # GET
    path('login/', views.LoginView.as_view(), name='login'),       # POST
    path('logout/', views.LogOutView.as_view(), name='logout'),       # POST
    # path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile-detail'),  # GET
    # path('profile/', views.ProfileView.as_view(), name='profile-detail'),  # POST
    path('student_profile/<int:pk>/', views.StudentProfileView.as_view(), name='student-profile-detail'), # GET
    path('student_profile/', views.StudentProfileView.as_view(), name='student-profile-detail'),  # POST

    path('teacher_profile/<int:pk>/', views.TeacherProfileView.as_view(), name='teacher-profile-detail'),  # GET
    path('teacher_profile/', views.TeacherProfileView.as_view(), name='teacher-profile-detail'),  # POST

    path('parent_profile/<int:pk>/', views.ParentProfileView.as_view(), name='parent-profile-detail'),  # GET
    path('parent_profile/', views.ParentProfileView.as_view(), name='parent-profile-detail'),  # POST

    path('staff_profile/<int:pk>/', views.StaffProfileView.as_view(), name='staff-profile-detail'),  # GET
    path('staff_profile/', views.StaffProfileView.as_view(), name='staff-profile-detail'),  # POST

      
]