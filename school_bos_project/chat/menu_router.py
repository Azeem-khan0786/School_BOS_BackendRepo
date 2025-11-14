from .menus import MENUS, get_menu_text
from .state_manager import (
    get_user_state, set_user_state, touch_state, is_session_stale,
    get_selected_student, set_selected_student
)
from Account.models import StudentProfile
from .handlers import (
    attendance_handler, fees_handler, marks_handler,
    exams_handler, library_handler, notices_handler, summary_handler
)
from chat.lang_manager import get_lang_text


SHORTCUTS = {
    "attendance": "attendance_menu",
    "fees": "fees_menu",
    "marks": "marks_menu",
    "exams": "exams_menu",
    "library": "library_menu",
    "notices": "notices_menu",
    "today": "attendance_today",
    "report": "summary_now",
    "help": "main_menu",
    "menu": "main_menu",
    "switch": "switch_student",
    "language": "language_switch_prompt"
}


# 🔹 Get menu text dynamically in preferred language
def _format_menu_text(key: str, student, lang="English"):
    """
    Builds menu text dynamically using the correct language file.
    Falls back to English if translation key not found.
    """
    translated = get_lang_text(key, lang)
    if translated.startswith("[Missing"):
        text = get_lang_text(key, "English")  # fallback to English
    else:
        text = translated

    student_name = f"{student.user.username}" if student else "—"
    class_sec = f"{student.class_name}{student.section_name}" if student else "—"

    return (
        text.format(student_name=student_name, class_sec=class_sec)
        + "\n\n"
        + get_lang_text("change_language_footer", lang)
    )


def _prompt_student_list(children):
    msg = "👨‍👩‍👧 Please choose the student:\n"
    for i, c in enumerate(children, 1):
        msg += f"{i}️⃣ {c.user.username} ({c.class_name}{c.section_name})\n"
    msg += "\nReply with a number."
    return msg


def handle_menu_navigation(phone, text, user=None):
    text = (text or "").strip().lower()
    touch_state(phone)

    # 🔤 detect language preference
    lang = getattr(user, "language_preference", "English") or "English"

    # 🧍 parent-only access
    if not user or user.role != "parent":
        return "⚠️ Access restricted. Only registered parents can use this service."

    # 🌍 language switch flow
    if text == "language":
        return get_lang_text("language_switch_prompt", lang)

    if text.lower() in ["hindi", "english"]:
        user.language_preference = text.title()
        user.save(update_fields=["language_preference"])
        lang = user.language_preference  # refresh

        reply = get_lang_text("language_switched", lang)
        selected = get_selected_student(phone)
        if selected:
            reply += "\n\n" + get_lang_text("main_menu", lang).format(
                student_name=selected.user.username,
                class_sec=f"{selected.class_name}{selected.section_name}"
            )
            reply += "\n\n" + get_lang_text("change_language_footer", lang)
        return reply

    # 🎓 Get selected student
    selected = get_selected_student(phone)
    children = StudentProfile.objects.filter(parent__user=user).order_by("id")
    if not children.exists():
        return "No students found under your account. Please contact the school."

    # 🕒 Reset stale session
    if is_session_stale(phone, minutes=10):
        set_user_state(phone, "main_menu")

    # 👶 First-time setup
    if not selected:
        if children.count() == 1:
            set_selected_student(phone, children.first().id)
            set_user_state(phone, "main_menu")
            return (
                f"✅ Selected *{children.first().user.username} ({children.first().class_name}{children.first().section_name})*\n\n"
                + _format_menu_text("main_menu", children.first(), lang)
            )
        set_user_state(phone, "select_student")
        return _prompt_student_list(children)

    # 🚀 Global shortcuts
    if text in SHORTCUTS:
        action = SHORTCUTS[text]

        # switch child
        if action == "switch_student":
            set_user_state(phone, "select_student")
            return _prompt_student_list(children)

        # quick summary
        if action == "summary_now":
            return summary_handler.handle(phone, user, selected)

        # menu jumps
        if action in MENUS:
            set_user_state(phone, action)
            return _format_menu_text(action, selected, lang)

        # direct handler (attendance_today, etc.)
        if action.startswith("attendance_"):
            return _wrap_with_footer(attendance_handler.handle(phone, user, action, selected), selected)

    # 🧭 Menu navigation
    state = get_user_state(phone)
    current_menu = state.current_menu
    menu_data = MENUS.get(current_menu, MENUS["main_menu"])
    options = menu_data.get("options", {})

    # child selection flow
    if current_menu == "select_student":
        try:
            index = int(text) - 1
            chosen = list(children)[index]
            set_selected_student(phone, chosen.id)
            set_user_state(phone, "main_menu")
            return (
                f"✅ Selected *{chosen.user.username} ({chosen.class_name}{chosen.section_name})*\n\n"
                + _format_menu_text("main_menu", chosen, lang)
            )
        except (ValueError, IndexError):
            return "❌ That doesn’t match any option. Please reply with a valid number."

    # option navigation inside menu
    if text in options:
        next_action = options[text]
        if next_action in MENUS:
            set_user_state(phone, next_action)
            return _format_menu_text(next_action, selected, lang)

        # handler calls
        if next_action.startswith("attendance_"):
            return _wrap_with_footer(attendance_handler.handle(phone, user, next_action, selected), selected)
        if next_action.startswith("fees_"):
            return _wrap_with_footer(fees_handler.handle(phone, user, next_action, selected), selected)
        if next_action.startswith("marks_"):
            return _wrap_with_footer(marks_handler.handle(phone, user, next_action, selected), selected)
        if next_action.startswith("exams_"):
            return _wrap_with_footer(exams_handler.handle(phone, user, next_action, selected), selected)
        if next_action.startswith("library_"):
            return _wrap_with_footer(library_handler.handle(phone, user, next_action, selected), selected)
        if next_action.startswith("notices_"):
            return _wrap_with_footer(notices_handler.handle(phone, user, next_action, selected), selected)

    # ❌ Invalid input fallback
    return (
        get_lang_text("invalid_option", lang)
        + "\n\n"
        + _format_menu_text(current_menu, selected, lang)
    )


def _wrap_with_footer(msg: str, student):
    footer = (
        f"\n\nCurrently viewing: *{student.user.username} ({student.class_name}{student.section_name})*\n"
        "Type *menu* to go back or *switch* to change student."
    )
    return f"{msg}{footer}"
