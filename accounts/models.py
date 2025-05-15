from django.db import models
from django.contrib.auth.models import User
from structure.models import StudentStructure  # استيراد StudentStructure من تطبيق structure

# نموذج Student
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=11, unique=True)
    national_id = models.CharField(max_length=14, unique=True)
    structure = models.ForeignKey(StudentStructure, on_delete=models.SET_NULL, null=True, blank=True) # ودا كمان محتاج فيوز

    def get_my_courses(self):
        from courses.models import Course
        if self.structure:
            return Course.objects.filter(
                department=self.structure.department,
                academic_year=self.structure.year,
                semester=self.structure.semester
            )
        return Course.objects.none()  # المفروض نظبطها ف فايل الفيوز

    def __str__(self):
        return self.name

# نموذج Doctor
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=11, unique=True)
    national_id = models.CharField(max_length=14, unique=True)
    structure = models.ManyToManyField('structure.StudentStructure', blank=True) # ودة كمان

    def get_my_courses(self):
        from courses.models import Course
        return Course.objects.filter(doctor=self) # وده كماننن

    def __str__(self):
        return self.name
