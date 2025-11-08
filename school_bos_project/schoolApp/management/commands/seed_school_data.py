from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta

from Account.models import (
    User, StudentProfile, TeacherProfile, ParentProfile, StaffProfile
)
from schoolApp.models import (
    Subject, ClassRoom, Class, Book, BookIssue, AdmissionInquiry,
    Attendance, Notice, FeeModel, FAQ, Homework,
    Exam, ExamSubject, Grade, ReportCard
)

fake = Faker()

class Command(BaseCommand):
    help = "Safely seed all school data with connected fake entries."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🚀 Starting idempotent fake data generation..."))

        # === SUBJECTS ===
        subjects = []
        for name in ["Mathematics", "Science", "English", "History", "Geography", "Physics", "Chemistry", "Biology"]:
            subj, _ = Subject.objects.get_or_create(
                subject=name,
                defaults={
                    "code": f"{name[:3].upper()}{fake.random_int(100,999)}",
                    "description": fake.text(50)
                }
            )
            subjects.append(subj)
        self.stdout.write(self.style.SUCCESS(f"✅ Subjects OK ({len(subjects)})"))

        # === CLASSROOMS ===
        classrooms = []
        for i in range(1, 6):
            room, _ = ClassRoom.objects.get_or_create(
                class_room=f"LTU{i}",
                defaults={
                    "capacity": random.randint(30, 50),
                    "location": f"Block {random.choice(['A','B','C'])}",
                    "facilities": random.sample(
                        ['blackboard','whiteboard','projector','smart_board','digital_display'],
                        k=random.randint(1,3)
                    )
                }
            )
            classrooms.append(room)
        self.stdout.write(self.style.SUCCESS("✅ Classrooms OK"))

        # === HELPER TO CREATE USERS SAFELY ===
        def create_user(role):
            username = fake.unique.user_name()
            email = fake.unique.email()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "password": "password123",
                    "role": role,
                    "phone_number": fake.phone_number(),
                    "gender": random.choice(["Male", "Female"]),
                    "address": fake.address(),
                }
            )
            return user

        # === PARENTS ===
        parents = []
        for _ in range(10):
            user = create_user("parent")
            parent, _ = ParentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "phone_number": fake.phone_number(),
                    "relation": random.choice(["father","mother","guardian"]),
                    "occupation": fake.job()
                }
            )
            parents.append(parent)
        self.stdout.write(self.style.SUCCESS("✅ Parents OK"))

        # === TEACHERS ===
        teachers = []
        for _ in range(8):
            user = create_user("teacher")
            teacher, _ = TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "staff_id": f"TCH{fake.unique.random_int(1000,9999)}",
                    "department": fake.word().capitalize() + " Dept",
                    "qualification": random.choice(["B.Ed","M.Ed","PhD"]),
                    "joining_date": fake.date_this_decade(),
                }
            )
            teacher.subjects.set(random.sample(subjects, k=random.randint(1,3)))
            teachers.append(teacher)
        self.stdout.write(self.style.SUCCESS("✅ Teachers OK"))

        # === CLASSES ===
        classes = []
        for i in range(6, 11):
            cls, _ = Class.objects.get_or_create(
                class_name=f"Class {i}",
                section=random.choice(["A","B"]),
                defaults={
                    "student_count": random.randint(20,40),
                    "max_seats": 40
                }
            )
            cls.subjects.set(random.sample(subjects, k=random.randint(3,5)))
            cls.classrooms.set(random.sample(classrooms, k=1))
            classes.append(cls)
        self.stdout.write(self.style.SUCCESS("✅ Classes OK"))

        # === STUDENTS ===
        students = []
        for _ in range(40):
            user = create_user("student")
            student, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "admission_number": f"ADM{fake.unique.random_int(1000,9999)}",
                    "admission_date": fake.date_this_decade(),
                    "class_name": random.choice(classes).class_name,
                    "section_name": random.choice(["A","B"]),
                    "parent": random.choice(parents) if parents else None
                }
            )
            students.append(student)
        self.stdout.write(self.style.SUCCESS("✅ Students OK"))

        # === STAFF ===
        for _ in range(5):
            user = create_user("staff")
            StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    "staff_id": f"STF{fake.unique.random_int(1000,9999)}",
                    "designation": random.choice(["Librarian","Accountant","Clerk"]),
                    "joining_date": fake.date_this_decade(),
                }
            )
        self.stdout.write(self.style.SUCCESS("✅ Staff OK"))

        # === BOOKS ===
        books = []
        for _ in range(15):
            book, _ = Book.objects.get_or_create(
                isbn=fake.unique.isbn13(),
                defaults={
                    "title": fake.sentence(nb_words=3),
                    "author": fake.name(),
                    "category": random.choice(["Fiction","Science","Math","History"]),
                    "quantity": random.randint(1,5),
                    "available_copies": random.randint(1,5),
                }
            )
            books.append(book)
        self.stdout.write(self.style.SUCCESS("✅ Books OK"))

        # === EXAMS ===
        exams = []
        for cls in classes:
            exam, _ = Exam.objects.get_or_create(
                name=f"{cls.class_name} Mid Term",
                class_name=cls,
                academic_year="2025-26",
                term="Term 1",
                defaults={
                    "exam_type": random.choice(["mid_term","final","quiz"]),
                    "exam_date": timezone.now().date() - timedelta(days=random.randint(5,15)),
                    "end_date": timezone.now().date() - timedelta(days=random.randint(1,3)),
                    "total_marks": 100,
                }
            )
            for subj in random.sample(subjects, k=random.randint(3,5)):
                ExamSubject.objects.get_or_create(
                    exam=exam,
                    subject=subj,
                    defaults={
                        "max_marks": 100,
                        "exam_duration": timedelta(hours=2),
                    }
                )
            exams.append(exam)
        self.stdout.write(self.style.SUCCESS("✅ Exams OK"))

        # === GRADES & REPORT CARDS ===
        for student in random.sample(students, k=min(20, len(students))):
            for exam in random.sample(exams, k=2):
                for subj in random.sample(subjects, k=3):
                    Grade.objects.get_or_create(
                        student=student,
                        exam=exam,
                        subject=subj,
                        defaults={
                            "marks_obtained": random.randint(35,100),
                            "max_marks": 100,
                        }
                    )
                ReportCard.objects.get_or_create(student=student, exam=exam)
        self.stdout.write(self.style.SUCCESS("✅ Grades & Reports OK"))

        # === OTHER MODELS ===
        for _ in range(10):
            Notice.objects.get_or_create(
                title=fake.sentence(),
                defaults={
                    "message": fake.text(100),
                    "audience_type": random.sample(["All","Students","Teachers","Parents"], k=2)
                }
            )
            AdmissionInquiry.objects.create(
                student_name=fake.name(),
                parent_name=fake.name(),
                contact_number=fake.phone_number(),
                email=fake.email(),
                class_name=random.choice(classes).class_name,
                message=fake.text(100)
            )
            FAQ.objects.create(
                questions=fake.sentence(nb_words=6),
                answer=fake.text(80)
            )
        self.stdout.write(self.style.SUCCESS("✅ Notices, Inquiries, FAQs OK"))

        # === FEES, ATTENDANCE ===
        for student in random.sample(students, k=min(25, len(students))):
            FeeModel.objects.get_or_create(
                student=student.user,
                defaults={
                    "total_amount": random.randint(1000,5000),
                    "paid_amount": random.randint(500,4000),
                    "due_date": timezone.now().date() + timedelta(days=10),
                    "status": random.choice(["Paid","Panding"])
                }
            )
            Attendance.objects.get_or_create(
                student=student.user,
                date=timezone.now().date(),
                defaults={
                    "status": random.choice(["Present","Absent"]),
                    "remark": fake.text(20)
                }
            )
        self.stdout.write(self.style.SUCCESS("✅ Fees & Attendance OK"))

        # === HOMEWORK ===
        for teacher in teachers:
            for _ in range(2):
                Homework.objects.get_or_create(
                    teacher=teacher.user,
                    title=fake.sentence(),
                    defaults={
                        "class_name": random.choice(classes),
                        "description": fake.text(100),
                        "subject": random.choice(subjects).subject,
                        "due_date": timezone.now().date() + timedelta(days=random.randint(3,10)),
                        "assignment_type": random.choice(["class","student"]),
                    }
                )
        self.stdout.write(self.style.SUCCESS("✅ Homework OK"))

        # === BOOK ISSUES ===
        for student in random.sample(students, k=min(10, len(students))):
            book = random.choice(books)
            if book.available_copies > 0:
                try:
                    BookIssue.objects.get_or_create(
                        book=book,
                        issued_to=student.user,
                        defaults={
                            "issue_date": timezone.now().date() - timedelta(days=5),
                            "due_date": timezone.now().date() + timedelta(days=5),
                        }
                    )
                    book.available_copies -= 1
                    book.save()
                except Exception:
                    continue
        self.stdout.write(self.style.SUCCESS("✅ Book Issues OK"))

        self.stdout.write(self.style.SUCCESS("\n🎉 ALL FAKE DATA SEEDED SUCCESSFULLY — SAFE TO RE-RUN ANYTIME!"))
