from django.db import models
from accounts.models import Doctor, Student
from structure.models import DepartmentChoices, AcademicYearChoices, SemesterChoices

class Course(models.Model):
    name = models.CharField(max_length=255)  # اسم المادة
    department = models.CharField(
        max_length=25,
        choices=DepartmentChoices.choices
    )  # القسم باستخدام DepartmentChoices
    academic_year = models.CharField(max_length=6, choices=AcademicYearChoices.choices)  # السنة الدراسية
    semester = models.CharField(max_length=6, choices=SemesterChoices.choices)  # الترم
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)  # الدكتور المسؤول
    drive_link = models.URLField(max_length=500, blank=True, null=True)  # رابط جوجل درايف للمادة (اختياري)

    def __str__(self):
        return f"{self.name} - {self.get_department_display()} - {self.academic_year} - {self.semester}"


# جدول يربط الطالب بالمواد بناءً على هيكل الطالب
class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # الطالب
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # المادة

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"
