from django.core.mail import send_mail
from django.conf import settings

def send_email_to_student():
    subject = "Book Issue Request Feedback"
    message = "Hey Sovon!\nThe book is available. You can collect it anytime.\n\nThank You!"
    from_email = settings.EMAIL_HOST_USER
    student_list = ["emondeveloper@gmail.com"]
    send_mail(subject, message, from_email, student_list)