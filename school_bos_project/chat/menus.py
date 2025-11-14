from chat.lang_manager import get_lang_text

def get_menu_text(menu_key, lang, student=None):
    """Fetch localized menu text and format placeholders."""
    return get_lang_text(menu_key, lang).format(
        student_name=student.user.username if student else "",
        class_sec=f"{student.class_name}{student.section_name}" if student else ""
    )


MENUS = {
    "main_menu": {
        "text": (
            "🏫 *SchoolBot — Main Menu*\n"
            "You're viewing: *{student_name}* ({class_sec})\n\n"
            "1️⃣ Attendance 📅\n"
            "2️⃣ Fees 💰\n"
            "3️⃣ Marks 🧮\n"
            "4️⃣ Exams 📘\n"
            "5️⃣ Library 📚\n"
            "6️⃣ Notices 📢\n\n"
            "💡 Shortcuts: *today*, *fees*, *marks*, *report*, *switch*, *help*\n"
            "Type a number (1–6) or a shortcut."
        ),
        "options": {
            "1": "attendance_menu",
            "2": "fees_menu",
            "3": "marks_menu",
            "4": "exams_menu",
            "5": "library_menu",
            "6": "notices_menu",
        },
    },

    "attendance_menu": {
        "text": (
            "📅 *Attendance Options*\n"
            "1️⃣ Today\n"
            "2️⃣ This Month\n"
            "3️⃣ Overall %\n"
            "0️⃣ Back\n\n"
            "Tip: type *today* anytime."
        ),
        "options": {
            "1": "attendance_today",
            "2": "attendance_month",
            "3": "attendance_percentage",
            "0": "main_menu",
        },
    },

    "fees_menu": {
        "text": (
            "💰 *Fees Options*\n"
            "1️⃣ Summary\n"
            "2️⃣ Paid\n"
            "3️⃣ Pending\n"
            "0️⃣ Back\n\n"
            "Tip: type *fees* anytime."
        ),
        "options": {
            "1": "fees_summary",
            "2": "fees_paid",
            "3": "fees_due",
            "0": "main_menu",
        },
    },

    "marks_menu": {
        "text": (
            "🧮 *Marks Options*\n"
            "1️⃣ Recent Marks\n"
            "2️⃣ Subject-wise Avg\n"
            "3️⃣ Overall Performance\n"
            "0️⃣ Back\n\n"
            "Tip: type *marks* or *report* anytime."
        ),
        "options": {
            "1": "marks_recent",
            "2": "marks_subjectwise",
            "3": "marks_overall",
            "0": "main_menu",
        },
    },
}
