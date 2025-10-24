Essential Information to Share:
ACCOUNT MODULE – API DOCUMENTATION
Base URL
http://127.0.0.1:8000/Account/url


POST    http://127.0.0.1:8000/Account/register/                 # Register new user
GET     http://127.0.0.1:8000/Account/register/<int:pk>/        # Get user details by ID

POST    http://127.0.0.1:8000/Account/login/                    # User login
POST    http://127.0.0.1:8000/Account/logout/                   # User logout

GET     http://127.0.0.1:8000/Account/profile/<int:pk>/         # Get profile details by ID
PUT     http://127.0.0.1:8000/Account/profile/<int:pk>/         # Update profile details
DELETE  http://127.0.0.1:8000/Account/profile/<int:pk>/         # Delete profile

GET     http://127.0.0.1:8000/Account/student_profile/<int:pk>/ # Get student profile details by ID
PUT     http://127.0.0.1:8000/Account/student_profile/<int:pk>/ # Update student profile details
DELETE  http://127.0.0.1:8000/Account/student_profile/<int:pk>/ # Delete student profile

GET     http://127.0.0.1:8000/Account/teacher_profile/<int:pk>/ # Get teacher profile details by ID
PUT     http://127.0.0.1:8000/Account/teacher_profile/<int:pk>/ # Update teacher profile details
DELETE  http://127.0.0.1:8000/Account/teacher_profile/<int:pk>/ # Delete teacher profile

GET     http://127.0.0.1:8000/Account/parent_profile/<int:pk>/  # Get parent profile details by ID
PUT     http://127.0.0.1:8000/Account/parent_profile/<int:pk>/  # Update parent profile details
DELETE  http://127.0.0.1:8000/Account/parent_profile/<int:pk>/  # Delete parent profile

GET     http://127.0.0.1:8000/Account/staff_profile/<int:pk>/   # Get staff profile details by ID
PUT     http://127.0.0.1:8000/Account/staff_profile/<int:pk>/   # Update staff profile details
DELETE  http://127.0.0.1:8000/Account/staff_profile/<int:pk>/   # Delete staff profile


Currently: Session-based
Frontend can manage login session via cookies (if using web).
If you plan to use mobile app or React frontend, better use JWT tokens.

Please check all using postman, exclude logout i have check for logout.






