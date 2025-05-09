from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Doctor

# Serializer لليوزر الأساسي (اللي بيحتوي على اليوزرنيم والإيميل مثلاً)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Serializer للطالب
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'name', 'mobile', 'national_id']

# Serializer للدكتور
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'name', 'mobile', 'national_id']
