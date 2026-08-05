from django.contrib import admin
from .models import Registration,Book,Student,IssueRecord,Notice

admin.site.register(Registration)
admin.site.register(Book)
admin.site.register(Student)
admin.site.register(IssueRecord)
admin.site.register(Notice)