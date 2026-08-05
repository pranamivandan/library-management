from django.urls import path
from . import views

urlpatterns = [
    path('',views.first,name='first'),
    path('third/', views.third, name='third'),
    path('reg/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('student/', views.student, name='student'),
    path('book/', views.book, name='book'),
    path('booklist/', views.booklist, name='booklist'),
    path('IssueRecord/', views.issue_record, name='IssueRecord'),
    path('IssueRecord/return/<int:id>/', views.return_book, name='return_book'),
    path('IssueRecord/delete/<int:id>/', views.delete_issue_record, name='delete_issue_record'),
    path('logout/', views.logout, name='logout'),
    path('homes/',views.homes,name='homes'),
    path('studentdesk/',views.studentdesk,name='studentdesk'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('mybook/',views.mybook,name='mybook'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('change-password/', views.change_password, name='change_password'),
    path('notice/', views.notice, name='notice'),
    path('library/', views.detaillibrary, name='detaillibrary'),
    
]