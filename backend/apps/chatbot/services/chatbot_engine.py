import re
from difflib import SequenceMatcher


INTENT_PATTERNS = {
    'check_results': {
        'patterns': [
            'my result', 'my results', 'check result', 'exam result', 'exam results',
            'term result', 'report card', 'grades', 'my grade', 'how did i do',
            'what did i score', 'my score', 'academic performance', 'check my result',
            'see my result', 'view result', 'view my result', 'result for', 'my marks',
        ],
        'min_role': ['STUDENT', 'PARENT'],
    },
    'check_fees': {
        'patterns': [
            'my fees', 'school fees', 'fee balance', 'how much do i owe',
            'fee status', 'payment status', 'outstanding fees', 'pay fees',
            'fee payment', 'have i paid', 'fee clearance', 'fees owed',
            'check fee', 'check fees', 'my balance', 'due fees',
        ],
        'min_role': ['STUDENT', 'PARENT'],
    },
    'check_attendance': {
        'patterns': [
            'my attendance', 'attendance record', 'how many days absent',
            'attendance status', 'check attendance', 'days present',
            'attendance percentage', 'am i present', 'attendance summary',
            'my attendance record', 'school attendance',
        ],
        'min_role': ['STUDENT', 'PARENT'],
    },
    'contact_teacher': {
        'patterns': [
            'contact teacher', 'talk to teacher', 'message teacher',
            'reach teacher', 'speak with teacher', 'send message to teacher',
            'talk to my child teacher', 'contact my child teacher',
        ],
        'min_role': ['PARENT'],
    },
    'report_issue': {
        'patterns': [
            'report issue', 'report a problem', 'complaint', 'make complaint',
            'report something', 'something wrong', 'problem with', 'issue with',
            'bullying', 'sick', 'health issue', 'emergency',
        ],
        'min_role': ['STUDENT', 'PARENT'],
    },
    'school_info': {
        'patterns': [
            'school info', 'school information', 'school address',
            'school hours', 'school time', 'when does school open',
            'school contact', 'school phone', 'school email',
            'term dates', 'school calendar', 'holiday dates',
        ],
        'min_role': ['STUDENT', 'PARENT', 'TEACHER'],
    },
    'timetable': {
        'patterns': [
            'my timetable', 'class timetable', 'school timetable',
            'what classes today', 'schedule today', 'today schedule',
            'next class', 'period timetable', 'weekly timetable',
        ],
        'min_role': ['STUDENT', 'TEACHER'],
    },
    'staff_directory': {
        'patterns': [
            'staff list', 'teacher list', 'all teachers', 'staff directory',
            'who teaches', 'subject teacher', 'list of teachers',
            'find teacher', 'search teacher',
        ],
        'min_role': ['STUDENT', 'PARENT', 'TEACHER'],
    },
    'announcement': {
        'patterns': [
            'announcement', 'latest news', 'school news', 'important notice',
            'what is happening', 'recent announcement', 'school update',
            'any news', 'what is new',
        ],
        'min_role': ['STUDENT', 'PARENT', 'TEACHER'],
    },
    'general_help': {
        'patterns': [
            'help', 'what can you do', 'how to use', 'what are your features',
            'commands', 'options', 'menu', 'guide', 'tutorial',
            'i need help', 'assist me', 'what do you know',
        ],
        'min_role': ['STUDENT', 'PARENT', 'TEACHER'],
    },
}


class ChatbotEngine:
    @staticmethod
    def detect_intent(message: str) -> dict:
        message_lower = message.lower().strip()
        best_intent = None
        best_score = 0.0

        for intent_name, intent_data in INTENT_PATTERNS.items():
            for pattern in intent_data['patterns']:
                score = SequenceMatcher(None, message_lower, pattern).ratio()
                if pattern in message_lower:
                    score = max(score, 0.85)
                if score > best_score:
                    best_score = score
                    best_intent = intent_name

        if best_score < 0.3:
            return {'intent': 'unknown', 'confidence': 0.0, 'min_role': []}

        return {
            'intent': best_intent,
            'confidence': round(best_score, 2),
            'min_role': INTENT_PATTERNS.get(best_intent, {}).get('min_role', []),
        }

    @staticmethod
    def get_response(intent: str, user=None, context: dict = None) -> str:
        responses = {
            'check_results': ChatbotEngine._handle_check_results,
            'check_fees': ChatbotEngine._handle_check_fees,
            'check_attendance': ChatbotEngine._handle_check_attendance,
            'contact_teacher': ChatbotEngine._handle_contact_teacher,
            'report_issue': ChatbotEngine._handle_report_issue,
            'school_info': ChatbotEngine._handle_school_info,
            'timetable': ChatbotEngine._handle_timetable,
            'staff_directory': ChatbotEngine._handle_staff_directory,
            'announcement': ChatbotEngine._handle_announcement,
            'general_help': ChatbotEngine._handle_general_help,
            'unknown': ChatbotEngine._handle_unknown,
        }
        handler = responses.get(intent, ChatbotEngine._handle_unknown)
        return handler(user, context)

    @staticmethod
    def _handle_check_results(user, context):
        if not user:
            return "Please log in to check your results."
        if user.role == 'STUDENT':
            from apps.students.models import Student, AcademicRecord
            student = Student.objects.filter(user=user).first()
            if not student:
                return "Student profile not found."
            records = AcademicRecord.objects.filter(student=student).order_by('-created_at')[:3]
            if not records:
                return "No results found yet."
            lines = ["Here are your recent results:\n"]
            for r in records:
                lines.append(f"• {r.subject}: {r.score}% ({r.grade})")
            lines.append(f"\nOverall Average: {records[0].average_score}%")
            return "\n".join(lines)
        elif user.role == 'PARENT':
            from apps.students.models import Student
            children = Student.objects.filter(parent__user=user)
            if not children:
                return "No children linked to your account."
            lines = ["Your children's recent results:\n"]
            for child in children[:3]:
                name = child.user.get_full_name()
                records = child.academic_records.all().order_by('-created_at')[:2]
                lines.append(f"**{name}**:")
                for r in records:
                    lines.append(f"  • {r.subject}: {r.score}% ({r.grade})")
            return "\n".join(lines)
        return "Results are available for students and parents only."

    @staticmethod
    def _handle_check_fees(user, context):
        if not user:
            return "Please log in to check fees."
        from apps.finance.models import FeeBalance
        if user.role == 'STUDENT':
            student = user.student_profile.first()
            if not student:
                return "Profile not found."
            fees = FeeBalance.objects.filter(student=student)
            if not fees:
                return "No fee records found."
            total_owed = sum(f.amount_owed - f.amount_paid for f in fees)
            lines = [f"**Fee Balance**: NGN {total_owed:,.2f}"]
            for f in fees:
                status = "Paid" if f.amount_paid >= f.amount_owed else f"NGN {f.amount_owed - f.amount_paid:,.2f} outstanding"
                lines.append(f"• {f.fee_type}: {status}")
            return "\n".join(lines)
        return "Fee information is available for students and parents."

    @staticmethod
    def _handle_check_attendance(user, context):
        if not user:
            return "Please log in to check attendance."
        from apps.attendance.models import Attendance
        if user.role == 'STUDENT':
            student = user.student_profile.first()
            if not student:
                return "Profile not found."
            records = Attendance.objects.filter(student=student)
            total = records.count()
            present = records.filter(status='PRESENT').count()
            absent = records.filter(status='ABSENT').count()
            rate = (present / total * 100) if total > 0 else 0
            return (f"**Attendance Summary**\n"
                    f"• Days Present: {present}\n"
                    f"• Days Absent: {absent}\n"
                    f"• Attendance Rate: {rate:.1f}%")
        return "Attendance information is available for students and parents."

    @staticmethod
    def _handle_contact_teacher(user, context):
        return ("To contact a teacher, please use the Communication module in the portal, "
                "or visit the school admin office. You can send messages directly to any "
                "teacher through the portal's messaging feature.")

    @staticmethod
    def _handle_report_issue(user, context):
        return ("To report an issue:\n"
                "• **Academic issues**: Contact your class teacher or head of department\n"
                "• **Health/Safety emergencies**: Call the school nurse immediately\n"
                "• **Bullying**: Report to the Guidance & Counseling unit\n"
                "• **General complaints**: Use the portal's complaint form or visit the admin office")

    @staticmethod
    def _handle_school_info(user, context):
        from apps.schools.models import School
        schools = School.objects.all()[:5]
        lines = ["**School Information**\n"]
        for s in schools:
            lines.append(f"• **{s.name}**: {s.address or 'No address set'}")
        lines.append("\n**Portal Hours**: 24/7 online access")
        lines.append("**Support Hours**: Mon-Fri, 8:00 AM - 4:00 PM")
        return "\n".join(lines)

    @staticmethod
    def _handle_timetable(user, context):
        return ("To view your timetable, go to the **Timetable** section in the portal. "
                "You can view daily, weekly, and termly schedules there.")

    @staticmethod
    def _handle_staff_directory(user, context):
        from apps.users.models import User
        teachers = User.objects.filter(role='TEACHER').select_related('school')[:10]
        lines = ["**Staff Directory** (showing 10):\n"]
        for t in teachers:
            school = t.school.name if t.school else 'Unassigned'
            lines.append(f"• {t.get_full_name()} - {school}")
        lines.append(f"\n... and {User.objects.filter(role='TEACHER').count() - 10} more teachers.")
        lines.append("Use the Staff module to search for specific teachers.")
        return "\n".join(lines)

    @staticmethod
    def _handle_announcement(user, context):
        from apps.communication.models import Communication
        comms = Communication.objects.filter(communication_type='ANNOUNCEMENT').order_by('-created_at')[:3]
        if not comms:
            return "No recent announcements."
        lines = ["**Recent Announcements**\n"]
        for c in comms:
            lines.append(f"• **{c.title}** ({c.created_at.strftime('%d %b %Y')})\n  {c.message[:100]}...")
        return "\n".join(lines)

    @staticmethod
    def _handle_general_help(user, context):
        role = user.role if user else 'GUEST'
        help_text = {
            'STUDENT': (
                "**What I can help you with:**\n"
                "• 📊 Check your exam results and grades\n"
                "• 💰 View fee balances and payment status\n"
                "• 📅 Check your attendance record\n"
                "• 📋 View your class timetable\n"
                "• 📢 See latest school announcements\n"
                "• 📝 Report issues or concerns\n"
                "• 🏫 Get school information\n\n"
                "Just type what you need naturally!"
            ),
            'PARENT': (
                "**What I can help you with:**\n"
                "• 📊 Check your children's results\n"
                "• 💰 View fee balances and payment status\n"
                "• 📅 Check attendance records\n"
                "• 📞 Get contact information for teachers\n"
                "• 📢 See latest school announcements\n"
                "• 📝 Report issues about your child\n"
                "• 🏫 Get school information\n\n"
                "Just type what you need naturally!"
            ),
            'TEACHER': (
                "**What I can help you with:**\n"
                "• 📋 View your teaching timetable\n"
                "• 👥 Staff directory and contacts\n"
                "• 📢 See latest school announcements\n"
                "• 🏫 Get school information\n\n"
                "Just type what you need naturally!"
            ),
            'GUEST': (
                "**Welcome to the Education District IV Chatbot!**\n"
                "I can help with:\n"
                "• 📊 Student results and grades\n"
                "• 💰 Fee information\n"
                "• 📅 Attendance records\n"
                "• 🏫 School information\n"
                "• 📢 Announcements\n\n"
                "Please log in for personalized assistance!"
            ),
        }
        return help_text.get(role, help_text['GUEST'])

    @staticmethod
    def _handle_unknown(user, context):
        return ("I'm not sure I understand. Here are some things I can help with:\n"
                "• Check exam results\n"
                "• View fee balances\n"
                "• Check attendance\n"
                "• School information\n"
                "• Announcements\n\n"
                "Try asking in a different way, or type 'help' for more options.")

    @staticmethod
    def _get_suggestions(role):
        suggestions = {
            'STUDENT': [
                'Check my results',
                'View my fees',
                'My attendance',
                'View timetable',
                'School announcements',
            ],
            'PARENT': [
                "My child's results",
                'Fee balance',
                'Check attendance',
                'Contact teacher',
                'School announcements',
            ],
            'TEACHER': [
                'View timetable',
                'Staff directory',
                'School announcements',
                'School information',
            ],
        }
        return suggestions.get(role, ['Help', 'School information', 'Announcements'])
