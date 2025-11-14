from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from Account.models import User, StudentProfile
from schoolApp.models import Attendance, FeeModel, Grade
from chat.menu_router import handle_menu_navigation
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
        if request.GET.get("hub.verify_token") == settings.VERIFY_TOKEN:
            return HttpResponse(request.GET.get("hub.challenge"))
        return HttpResponse("Invalid verification token", status=403)

    if request.method == "POST":
        payload = request.data
        try:
            message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            phone = message["from"]
            text = message.get("text", {}).get("body", "").strip()
        except (KeyError, IndexError):
            return Response(status=200)

        user = User.objects.filter(phone_number__icontains=phone[-10:]).first()
        if not user:
            send_whatsapp_text(phone, "User not found. Please contact admin.")
            return Response(status=200)

        reply = handle_menu_navigation(phone, text, user)
        send_whatsapp_text(phone, reply)
        return Response(status=200)
