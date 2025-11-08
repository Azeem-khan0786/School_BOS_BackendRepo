from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from Account.models import User, StudentProfile
from schoolApp.models import Attendance, FeeModel, Grade

from .utility import send_whatsapp_message, send_message_service, send_whatsapp_text


@api_view(["POST"])
def send_template_message(request):
    """
    Universal WhatsApp send endpoint.
    Works with simplified variable-only JSON payloads.

    Example:
    {
        "phone": "919876543210",
        "template_name": "test_template",
        "language": "en",
        "variables": {"1": "John"},
        "buttons": [{ "type": "quick_reply", "text": "Thank you" }]
    }
    """
    try:
        data = request.data
        phone = data.get("phone")
        template_name = data.get("template_name")
        language = data.get("language", "en")
        variables = data.get("variables", {})
        buttons = data.get("buttons", [])

        if not phone or not template_name:
            return Response(
                {"error": "phone and template_name are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Delegate to shared service used internally & externally
        result = send_message_service(
            template_name=template_name,
            phone=phone,
            variables=variables,
            language=language,
            buttons=buttons
        )

        code = 200 if result.get("status") == "success" else 400
        return Response(result, status=code)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    if request.method == "GET":
        verify_token = settings.VERIFY_TOKEN
        if request.GET.get("hub.verify_token") == verify_token:
            return HttpResponse(request.GET.get("hub.challenge"))
        return HttpResponse("Invalid verification token", status=403)

    if request.method == "POST":
        payload = request.data
        print("📩 Incoming WhatsApp Webhook:", payload)

        try:
            message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            phone = message["from"]
            text = message.get("text", {}).get("body", "").strip().lower()
        except (KeyError, IndexError):
            return Response(status=status.HTTP_200_OK)

        # Identify linked user
        from Account.models import User
        user = User.objects.filter(phone_number__icontains=phone[-10:]).first()

        if not user:
            send_whatsapp_text(phone, "We couldn’t find your account. Please contact school admin.")
            return Response(status=status.HTTP_200_OK)

        

        if text in ["menu", "hi", "hello"]:
            body = (
                "📘 *SchoolBot Menu*\n\n"
                "1️⃣ Attendance → type *attendance*\n"
                "2️⃣ Fees → type *fees*\n"
                "3️⃣ Marks → type *marks*\n"
                "4️⃣ Help → type *menu*\n"
            )
            send_whatsapp_text(phone, body)
            return Response(status=status.HTTP_200_OK)

        # ✅ Attendance
        if text == "attendance":
            today = timezone.now().date()
            if user.role == "student":
                record = Attendance.objects.filter(student=user, date=today).first()
                if record:
                    msg = f"📅 Attendance for {today}:\nStatus: *{record.status}*\nRemark: {record.remark or '—'}"
                else:
                    msg = f"No attendance record found for {today}."
                send_whatsapp_text(phone, msg)
                return Response(status=status.HTTP_200_OK)

            elif user.role == "parent":
                children = StudentProfile.objects.filter(parent__user=user)
                if not children.exists():
                    send_whatsapp_text(phone, "No students linked to your account.")
                    return Response(status=status.HTTP_200_OK)
                reply = "📅 *Today's Attendance:*\n"
                for c in children:
                    rec = Attendance.objects.filter(student=c.user, date=today).first()
                    status_text = rec.status if rec else "Not marked"
                    reply += f"\n👧 {c.user.username}: {status_text}"
                send_whatsapp_text(phone, reply)
                return Response(status=status.HTTP_200_OK)

            else:
                send_whatsapp_text(phone, "Attendance details are available for students and parents only.")
                return Response(status=status.HTTP_200_OK)

        # ✅ Fees
        if text == "fees":
            if user.role == "student":
                fee = FeeModel.objects.filter(student=user).last()
                if fee:
                    msg = (
                        f"💰 *Fee Summary*\n"
                        f"Total: ₹{fee.total_amount}\nPaid: ₹{fee.paid_amount}\n"
                        f"Due: ₹{float(fee.total_amount) - float(fee.paid_amount)}\n"
                        f"Due Date: {fee.due_date}\nStatus: {fee.status}"
                    )
                else:
                    msg = "No fee record found."
                send_whatsapp_text(phone, msg)
                return Response(status=status.HTTP_200_OK)

            elif user.role == "parent":
                children = StudentProfile.objects.filter(parent__user=user)
                if not children.exists():
                    send_whatsapp_text(phone, "No students linked to your account.")
                    return Response(status=status.HTTP_200_OK)
                reply = "💰 *Fee Summary:*\n"
                for c in children:
                    fee = FeeModel.objects.filter(student=c.user).last()
                    if fee:
                        reply += (
                            f"\n👧 {c.user.username}\n"
                            f"Total: ₹{fee.total_amount}\nPaid: ₹{fee.paid_amount}\n"
                            f"Due Date: {fee.due_date}\nStatus: {fee.status}\n"
                        )
                    else:
                        reply += f"\n👧 {c.user.username}: No record found\n"
                send_whatsapp_text(phone, reply)
                return Response(status=status.HTTP_200_OK)

        # ✅ Marks
        if text == "marks":
            if user.role == "student":
                grades = Grade.objects.filter(student__user=user).order_by("-created_at")[:3]
                if not grades:
                    msg = "No marks available yet."
                else:
                    msg = "📊 *Recent Results:*\n"
                    for g in grades:
                        msg += f"{g.subject.subject}: {g.marks_obtained}/{g.max_marks} ({g.grade})\n"
                send_whatsapp_text(phone, msg)
                return Response(status=status.HTTP_200_OK)

            elif user.role == "parent":
                students = StudentProfile.objects.filter(parent__user=user)
                reply = "📊 *Recent Marks:*\n"
                for s in students:
                    grades = Grade.objects.filter(student=s).order_by("-created_at")[:2]
                    if grades:
                        reply += f"\n👧 {s.user.username}\n"
                        for g in grades:
                            reply += f"• {g.subject.subject}: {g.marks_obtained}/{g.max_marks} ({g.grade})\n"
                    else:
                        reply += f"\n👧 {s.user.username}: No marks found\n"
                send_whatsapp_text(phone, reply)
                return Response(status=status.HTTP_200_OK)

        # Default fallback
        send_whatsapp_text(phone, "Sorry, I didn’t understand. Type *menu* to see options.")
        return Response(status=status.HTTP_200_OK)
