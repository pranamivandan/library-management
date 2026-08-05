from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Registration, Student, Book, IssueRecord, Notice
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date


def admin_required(view_func):
    """Only allow logged-in users with is_admin=True (the library admin)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")

        user = Registration.objects.filter(id=user_id).first()
        if not user or not user.is_admin:
            messages.error(request, "You don't have permission to access the admin panel.")
            return redirect("studentdesk")

        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        gender = request.POST.get('rdo')
        address = request.POST.get('address', '').strip()

        if not username or not email or not password or not mobile or not gender or not address:
            messages.error(request, "Please fill all fields.")
            return render(request, 'index.html')

        if Registration.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'index.html')

        new_user = Registration.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            mobile=mobile,
            gender=gender,
            address=address
        )

        Student.objects.create(
            user=new_user,
            name=username,
            roll_no="",
            mobile=mobile,
            email=email,
            gender=gender,
            address=address
        )

        messages.success(request, "Registration Successful!")
        return redirect('login')

    return render(request, 'index.html')

def login(request):
    message = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = Registration.objects.get(username=username)

            if check_password(password, user.password):
                print(user.username, user.is_admin)
                request.session["user_id"] = user.id

                if user.is_admin:
                    return redirect("third")
                return redirect("studentdesk")
            else:
                message = "Invalid Username or Password"

        except Registration.DoesNotExist:
            message = "Invalid Username or Password"

    return render(request, "login.html", {"message": message})

def logout(request):
    request.session.flush()
    return redirect("first")

@admin_required
def third(request):

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "student":
            return redirect("student")

        elif action == "book":
            return redirect("book")

        elif action == "bookall":
            return redirect("booklist")

        elif action == "IssueRecord":
            return redirect("IssueRecord")

        elif action == "notice":
            return redirect("notice")

    context = {
        "total_students": Student.objects.count(),
        "total_books": Book.objects.count(),
        "issued_books": IssueRecord.objects.filter(returned=False).count(),
        "available_books": Book.objects.filter(is_available=True).count(),
    }

    return render(request, "third.html", context)


@admin_required
def student(request):
    if request.method == 'POST':
        action = request.POST.get("action")

        if action == 'back':
            return redirect('third')

        name = request.POST.get('name')
        roll = request.POST.get('roll')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        gender = request.POST.get('rdo')
        address = request.POST.get('address')

        Student.objects.create(
            name=name,
            roll_no=roll,
            email=email,
            mobile=mobile,
            gender=gender,
            address=address
        )

        messages.success(request, "Student added successfully!")

        return redirect('student')

    return render(request, "student.html")

@admin_required
def book(request):
    if request.method == 'POST':

        action = request.POST.get("action")

        if action == 'back':
            return redirect('third')

        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')

        Book.objects.create(
             title=title,
             author=author,
             description=description,
             is_available=is_available,
             image=image,
            )

        messages.success(request, "book added successfully!")
        return redirect('book')

    return render(request, "book.html")


@admin_required
def booklist(request):
    delete_id = request.GET.get('delete')
    if delete_id:
        Book.objects.filter(id=delete_id).delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('booklist')

    edit_id = request.GET.get('edit')
    edit_book = get_object_or_404(Book, id=edit_id) if edit_id else None

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        b = get_object_or_404(Book, id=book_id)
        b.title = request.POST.get('title')
        b.author = request.POST.get('author')
        b.is_available = request.POST.get('is_available') == 'on'

        new_image = request.FILES.get('image')
        if new_image:
            b.image = new_image

        b.save()

        messages.success(request, "Book updated successfully!")
        return redirect('booklist')

    books = Book.objects.all()
    return render(request, "booklist.html", {"books": books, "edit_book": edit_book})


@admin_required
def issue_record(request):

    if request.method == "POST":
        book_id = request.POST.get("book")
        student_id = request.POST.get("student")
        due_date = request.POST.get("due_date")

        book = get_object_or_404(Book, id=book_id)

        if not book.is_available:
            messages.error(request, "This book is not available.")
            return redirect("IssueRecord")

        IssueRecord.objects.create(
            book=book,
            student_id=student_id,
            due_date=due_date
        )

        book.is_available = False
        book.save()

        messages.success(request, "Book issued successfully.")
        return redirect("IssueRecord")

    books = Book.objects.filter(is_available=True)
    students = Student.objects.all()
    records = IssueRecord.objects.filter(returned=False)

    return render(request, "IssueRecord.html", {
        "books": books,
        "students": students,
        "records": records
    })

@admin_required
def return_book(request, id):
    record = get_object_or_404(IssueRecord, id=id)

    record.returned = True
    record.save()

    record.book.is_available = True
    record.book.save()

    messages.success(request, "Book returned successfully.")
    return redirect("IssueRecord")

@admin_required
def delete_issue_record(request, id):
    record = get_object_or_404(IssueRecord, id=id)

    # if the book wasn't returned yet, deleting the record should free the book again
    if not record.returned:
        record.book.is_available = True
        record.book.save()

    record.delete()

    messages.success(request, "Issue record deleted successfully.")
    return redirect("IssueRecord")

def homes(request):

    return render(request, 'homes.html')

def first(request):

    return render(request, 'first.html')
def mybook(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    student = Student.objects.filter(user_id=user_id).first()

    records = []
    if student:
        records = IssueRecord.objects.filter(student=student).order_by('-issue_date')

        today = date.today()
        for record in records:
            record.fine = 0
            if not record.returned and today > record.due_date:
                days_late = (today - record.due_date).days
                record.fine = days_late * 2   # ₹2 per day

    return render(request, 'mybook.html', {'records': records, 'student': student})



def studentdesk(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    student = None
    try:
        student = Student.objects.get(user_id=user_id)
    except Student.DoesNotExist:
        pass

    search = request.GET.get('search')
    books = Book.objects.all().order_by('-id')
    notices = Notice.objects.all().order_by('-created_at')[:5]
    total_fine = 0
    if student:
        Issued_Books = IssueRecord.objects.filter(student=student, returned=False).count()

        overdue_records = IssueRecord.objects.filter(student=student, returned=False)
        today = date.today()
        for record in overdue_records:
            if today > record.due_date:
                days_late = (today - record.due_date).days
                total_fine += days_late * 2   # ₹2 per day, badal sakte ho
    else:
        Issued_Books = 0

    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search)
        )

    total_books = books.count()
    available_books = books.filter(is_available=True).count()

    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'studentdesk.html', {
        'page_obj': page_obj,
        'total_books': total_books,
        'available_books': available_books,
        'search': search,
        'Issued_Books': Issued_Books,
        'student': student,
        'total_fine': total_fine,
        'notices': notices,
    })
def book_detail(request, id):

    book = get_object_or_404(Book, id=id)

    return render(request, "book_detail.html", {
        "book": book
    })

def myprofile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    student = Student.objects.filter(user_id=user_id).first()

    return render(request, 'myprofile.html', {'student': student})

def change_password(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(Registration, id=user_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not check_password(old_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect('change_password')

        if not new_password or len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password')

        user.password = make_password(new_password)
        user.save()

        messages.success(request, "Password changed successfully. Please login again.")
        request.session.flush()
        return redirect('login')

    return render(request, 'change_password.html')

@admin_required
def notice(request):
    delete_id = request.GET.get('delete')
    if delete_id:
        Notice.objects.filter(id=delete_id).delete()
        messages.success(request, "Notice deleted successfully!")
        return redirect('notice')

    if request.method == 'POST':
        action = request.POST.get("action")

        if action == 'back':
            return redirect('third')

        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, "Notice title cannot be empty.")
            return redirect('notice')

        Notice.objects.create(title=title)

        messages.success(request, "Notice added successfully!")
        return redirect('notice')

    notices = Notice.objects.all().order_by('-created_at')
    return render(request, "notice.html", {"notices": notices})

def detaillibrary(request):
    return render(request, 'detaillibrary.html')
