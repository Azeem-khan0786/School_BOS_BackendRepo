from schoolApp.models import Notice
from chat.lang_manager import get_lang_text

def handle(phone, user, action, student):
    """
    Parent-only — Fetches relevant school notices (bilingual).
    """
    lang = getattr(user, "language_preference", "English") or "English"

    if not student:
        return get_lang_text("select_student_first", lang)

    audience = "Parents"
    notices = Notice.objects.filter(audience_type__icontains=audience).order_by("-date")[:5]
    if not notices.exists():
        notices = Notice.objects.filter(audience_type__icontains="All")[:5]

    if not notices.exists():
        return get_lang_text("notices_no_data", lang)

    msg = f"{get_lang_text('notices_title', lang)}\n"
    msg += f"{get_lang_text('child_label', lang)}: {student.user.username}\n"

    for n in notices:
        msg += f"\n• {n.title}\n  {n.message[:60]}...\n"

    return msg
