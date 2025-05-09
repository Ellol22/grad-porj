from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , get_user_model
from .models import Student, Doctor
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode ,  urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password


# دالة للتحقق من صحة الإيميل
def validate_email_format(email):
    # اي حاجة @ اي حاجة .com
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

@csrf_exempt
@api_view(['POST'])
def api_sign_up(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')
    national_id = data.get('national_id')
    email = data.get('email')
    mobile = data.get('mobile')
    name = data.get('name') 

    # التحقق من صحة الإيميل
    if not validate_email_format(email):
        return Response({'error': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # ✅ خطوة التحقق من الباسورد
    try:
        validate_password(password)  # هيشوف لو الباسورد ضعيف ويرجع خطأ
    except ValidationError as e:
        return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # التحقق من تكرار اسم المستخدم
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

    # التحقق من النوع وتسجيل الطالب أو الطبيب
    if user_type == 'Student':  # Student
        try:
            student = Student.objects.get(national_id=national_id)
            if student.user:
                return Response({'error': 'This national ID is already registered with a Student account.'}, status=status.HTTP_400_BAD_REQUEST)


            user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
            user.is_active = False  # بنقوله انت مش مفعل لسة
            user.save()
            student.user = user
            student.mobile = mobile
            student.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"{settings.SITE_DOMAIN}/api/activate/{uid}/{token}/"
            # إرسال الإيميل
            send_mail(
                subject="activate your account ✉️",
                message=f"hello {user.username}!\n please, press the link to activate your account :\n{activation_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )


            return Response({'message': 'Student account created successfully.'}, status=status.HTTP_201_CREATED)

        except Student.DoesNotExist:
            return Response({'error': 'National ID not found in the student database.'}, status=status.HTTP_404_NOT_FOUND)

    elif user_type == 'Doctor':  # Doctor
        try:
            doctor = Doctor.objects.get(national_id=national_id)
            if doctor.user:
                return Response({'error': 'This national ID is already registered with a Doctor account.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
            user.is_active = False  # بنقوله انت مش مفعل لسة
            user.save()
            doctor.user = user
            doctor.mobile = mobile
            doctor.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"{settings.SITE_DOMAIN}/api/activate/{uid}/{token}/"
            # إرسال الإيميل
            send_mail(
                subject="activate your account ✉️",
                message=f"hello {user.username}!\n please, press the link to activate your account :\n{activation_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({'message': 'Doctor account created successfully.'}, status=status.HTTP_201_CREATED)

        except Doctor.DoesNotExist:
            return Response({'error': 'National ID not found in the doctor database.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'error': 'Invalid user_type. Must be "Doctor" for Doctor or "Student" for Student.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_log_in(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    


User = get_user_model()
def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return JsonResponse({'message': 'تم تفعيل الحساب بنجاح ✅'})
    else:
        return JsonResponse({'message': 'رابط التفعيل غير صالح ❌'}, status=400)