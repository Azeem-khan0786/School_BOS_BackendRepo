from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings

from .utility import send_whatsapp_message, send_message_service


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
    """
    Webhook for Meta WhatsApp verification & event reception.
    """
    if request.method == "GET":
        verify_token = settings.VERIFY_TOKEN
        if request.GET.get("hub.verify_token") == verify_token:
            challenge = request.GET.get("hub.challenge")
            return HttpResponse(challenge)  # plain text for Meta verification
        return HttpResponse("Invalid verification token", status=403)

    if request.method == "POST":
        payload = request.data
        print("📩 Incoming WhatsApp Webhook:", payload)
        # TODO: handle message or status events here
        return Response(status=status.HTTP_200_OK)
