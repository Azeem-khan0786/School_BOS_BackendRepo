from schoolApp.models import FeeModel
from chat.lang_manager import get_lang_text

def handle(phone, user, action, student):
    """
    Parent-only — Handles child's fee details with bilingual (English/Hindi) support.
    """
    lang = getattr(user, "language_preference", "English") or "English"

    if not student:
        return get_lang_text("select_student_first", lang)

    fee = FeeModel.objects.filter(student=student.user).last()
    if not fee:
        return get_lang_text("fees_no_data", lang).format(name=student.user.username)

    due = float(fee.total_amount) - float(fee.paid_amount)

    # 🔸 ACTION: Fee Summary
    if action == "fees_summary":
        return (
            f"{get_lang_text('fees_summary_title', lang)}\n"
            f"{get_lang_text('child_label', lang)}: {student.user.username}\n"
            f"{get_lang_text('total_label', lang)}: ₹{fee.total_amount}\n"
            f"{get_lang_text('paid_label', lang)}: ₹{fee.paid_amount}\n"
            f"{get_lang_text('due_label', lang)}: ₹{due}\n"
            f"{get_lang_text('due_date_label', lang)}: {fee.due_date}\n"
            f"{get_lang_text('status_label', lang)}: {fee.status}"
        )

    # 🔸 ACTION: Paid details
    elif action == "fees_paid":
        return (
            f"{get_lang_text('fees_paid_title', lang)}\n"
            f"{get_lang_text('child_label', lang)}: {student.user.username}\n"
            f"{get_lang_text('paid_label', lang)}: ₹{fee.paid_amount}\n"
            f"{get_lang_text('status_label', lang)}: {fee.status}"
        )

    # 🔸 ACTION: Pending fees
    elif action == "fees_due":
        return (
            f"{get_lang_text('fees_due_title', lang)}\n"
            f"{get_lang_text('child_label', lang)}: {student.user.username}\n"
            f"{get_lang_text('pending_label', lang)}: ₹{due}\n"
            f"{get_lang_text('due_date_label', lang)}: {fee.due_date}"
        )

    return get_lang_text("invalid_option", lang)
