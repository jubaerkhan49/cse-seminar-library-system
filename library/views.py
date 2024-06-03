from library.forms import IssueBookForm
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from .models import *
from .forms import IssueBookForm, IssueRequestForm
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from datetime import date
from django.contrib.auth.decorators import login_required
from .utils  import send_email_to_student
from django.core.mail import send_mail
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)
def index(request):
    books = Book.objects.all()
    return render(request, "index.html", {'books':books})

@login_required(login_url = '/admin_login')
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']
        cover_page = request.FILES.get('cover_page')
        edition = request.POST['edition']
        is_available = request.POST['is_available'] == 'True'
        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category, cover_page=cover_page, edition=edition, is_available=is_available)
        books.save()
        alert = True
        return render(request, "add_book.html", {'alert':alert})
    return render(request, "add_book.html")

@login_required(login_url = '/admin_login')
def view_books(request):
    books = Book.objects.all()
    return render(request, "view_books.html", {'books':books})

@login_required(login_url = '/admin_login')
def view_students(request):
    students = Student.objects.all()
    return render(request, "view_students.html", {'students':students})

@login_required(login_url = '/admin_login')
def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.save()
            alert = True
            return render(request, "issue_book.html", {'obj':obj, 'alert':alert})
    return render(request, "issue_book.html", {'form':form})

@login_required(login_url = '/admin_login')
def view_issued_book(request):
    print("Jubaer")
    issuedBooks = IssuedBook.objects.all()
    details = []
    for issued in issuedBooks:
        days = (date.today() - issued.issued_date).days
        fine = 0
        if days > 14:
             fine = (days - 14) * 5
        # Fetch the book and student objects
        book = Book.objects.filter(isbn=issued.isbn).first()
        student = Student.objects.filter(user__id=issued.student_id).first()
        
        # Log if book or student is None
        if not book:
            logger.error(f"No book found with ISBN {issued.isbn}")
        if not student:
            logger.error(f"No student found with user ID {issued.student_id}")
        
        # Ensure both book and student are found before processing
        if book and student:
            detail = (
                student.user.get_full_name(),  # Student full name
                student.user_id,  # Student user id
                book.name,  # Book name
                book.isbn,  # Book ISBN
                issued.issued_date,  # Issue date
                issued.expiry_date,  # Expiry date
                fine,  # Fine
                issued.id
            )
            # print(detail)
            details.append(detail)
    return render(request, "view_issued_book.html", {'issuedBooks':issuedBooks, 'details':details})

@login_required(login_url='/admin_login')
def delete_issue(request, id):
    issued_book = get_object_or_404(IssuedBook, id=id)
    issued_book.delete()
    return redirect('view_issued_book')
@login_required(login_url = '/admin_login')
def send_email(request):
    send_email_to_student()
    return redirect('/')

@login_required(login_url = '/student_login')
def student_issued_books(request):
    student = Student.objects.filter(user_id=request.user.id)
    issuedBooks = IssuedBook.objects.filter(student_id=student[0].user_id)
    li1 = []
    li2 = []

    for i in issuedBooks:
        books = Book.objects.filter(isbn=i.isbn)
        for book in books:
            t=(request.user.id, request.user.get_full_name, book.name,book.author)
            li1.append(t)

        days=(date.today()-i.issued_date)
        d=days.days
        fine=0
        if d>15:
            day=d-14
            fine=day*5
        t=(issuedBooks[0].issued_date, issuedBooks[0].expiry_date, fine)
        li2.append(t)
    return render(request,'student_issued_books.html',{'li1':li1, 'li2':li2})

@login_required(login_url = '/student_login')
def profile(request):
    return render(request, "profile.html")

@login_required(login_url = '/student_login')
def edit_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']

        student.user.email = email
        student.phone = phone
        student.branch = branch
        student.classroom = classroom
        student.roll_no = roll_no
        student.user.save()
        student.save()
        alert = True
        return render(request, "edit_profile.html", {'alert':alert})
    return render(request, "edit_profile.html")

def delete_book(request, myid):
    books = Book.objects.filter(id=myid)
    books.delete()
    return redirect("/view_books")

def delete_student(request, myid):
    students = Student.objects.filter(id=myid)
    students.delete()
    return redirect("/view_students")

def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html")

def student_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            passnotmatch = True
            return render(request, "student_registration.html", {'passnotmatch':passnotmatch})

        user = User.objects.create_user(username=username, email=email, password=password,first_name=first_name, last_name=last_name)
        student = Student.objects.create(user=user, phone=phone, branch=branch, classroom=classroom,roll_no=roll_no, image=image)
        user.save()
        student.save()
        alert = True
        return render(request, "student_registration.html", {'alert':alert})
    return render(request, "student_registration.html")

def student_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return HttpResponse("You are not a student!!")
            else:
                return redirect("/profile")
        else:
            alert = True
            return render(request, "student_login.html", {'alert':alert})
    return render(request, "student_login.html")

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/add_book")
            else:
                return HttpResponse("You are not an admin.")
        else:
            alert = True
            return render(request, "admin_login.html", {'alert':alert})
    return render(request, "admin_login.html")

def Logout(request):
    logout(request)
    return redirect ("/")


# Added later to handle notifications
@login_required(login_url='/student_login')
def request_book(request):
    if request.method == 'POST':
        form = IssueRequestForm(request.POST)
        if form.is_valid():
            issue_request = form.save(commit=False)
            issue_request.student = request.user.student
            issue_request.save()
            alert = True
            return render(request, 'request_book.html', {'alert':alert})
    else:
        form = IssueRequestForm()
    return render(request, 'request_book.html', {'form': form})

@login_required(login_url='/admin_login')
def admin_panel(request):
    if not request.user.is_staff:
        return redirect('login')
    issue_requests = IssueRequest.objects.filter(status='Pending')
    books = Book.objects.all()
    return render(request, 'admin_panel.html', {'issue_requests': issue_requests})

@login_required(login_url='/admin_login')
def handle_request(request, request_id, action):
    if not request.user.is_staff:
        return redirect('login')
    issue_request = get_object_or_404(IssueRequest, id=request_id)
    student_name = issue_request.student.user.get_full_name()
    if action == 'accept':
        issue_request.status = 'Accepted'
        book = get_object_or_404(Book, id=issue_request.book.id)
        book.available = False
        book.save()
        message = f'Hey, {student_name}!\n' 
        message += f'Your request for the book "{issue_request.book.name}" has been accepted. You can collect it anytime!\n\nThank You.'
    else:
        issue_request.status = 'Rejected'
        message = f'Hey, {student_name}!\n' 
        message += f'Unfortunately, the book is not available at this moment. So your request for the book "{issue_request.book.name}" has been rejected.\n\nThank You.'
    issue_request.save()
    Notification.objects.create(student=issue_request.student, message=message)
    send_mail(
        'Book Issue Request',
        message,
        settings.EMAIL_HOST_USER,
        [issue_request.student.user.email],
        fail_silently=False,
    )
    return redirect('admin_panel')