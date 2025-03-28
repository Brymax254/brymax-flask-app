from flask import current_app
from app.models import Employee, Attendance
from .handlers import charts, payroll, attendance


def process_whatsapp_message(message, sender):
    """Main message processing router"""
    try:
        # Check if sender exists in system
        employee = Employee.query.filter_by(phone=sender).first()

        if not employee:
            return "Please register first using our web portal.", None

        # Command routing
        if message.startswith('chart'):
            return charts.handle_chart_request(message, employee)

        elif message.startswith('payroll'):
            return payroll.handle_payroll_request(employee)

        elif message.startswith('attendance'):
            return attendance.handle_attendance_request(employee)

        else:
            return help_message(), None

    except Exception as e:
        current_app.logger.error(f"WhatsApp bot error: {str(e)}")
        return "⚠️ Error processing request. Please try again.", None


def help_message():
    return (
        "Available commands:\n"
        "• chart <type> - Get visualization (bar/pie/line)\n"
        "• payroll - Get latest payroll info\n"
        "• attendance - Check attendance status\n"
        "• help - Show this menu"
    )