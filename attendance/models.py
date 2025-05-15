from django.db import models
from accounts.models import Student
from courses.models import Course
from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status_choices = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='absent')

    def _str_(self):
        return f"{self.student.name} - {self.course.name} - {self.date} - {self.get_status_display()}"


class QRCodeSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # الكورس
    code = models.CharField(max_length=10)  # الكود العشوائي
    created_at = models.DateTimeField(default=timezone.now)  # وقت الإنشاء
    image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)  # صورة الـ QR
    is_active = models.BooleanField(default=True)  # هل الكود لسه شغال؟

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 120  # الكود صالح لمدة دقيقتين

    def _str_(self):
        return f"{self.course.name} | Code: {self.code} | Time: {self.created_at.strftime('%H:%M:%S')}"