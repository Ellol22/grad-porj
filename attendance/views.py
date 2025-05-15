import random , os , qrcode , json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .models import QRCodeSession
from courses.models import Course
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2

def qr_generation_page(request, course_id):
    return render(request, 'generate_qr_live.html', {'course_id': course_id})

def generate_qr_code_ajax(request, course_id):
    course = Course.objects.get(id=course_id)
    random_number = random.randint(1000, 9999)
    qr_code_data = f"{random_number}"  # بس الرقم علشان الطالب يستخدمه

    qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_codes_dir, exist_ok=True)

    filename = f"qr_code_{int(datetime.now().timestamp())}.png"
    file_path = os.path.join(qr_codes_dir, filename)

    qr = qrcode.make(qr_code_data)
    qr.save(file_path)

    qr_session = QRCodeSession.objects.create(
        course=course,
        code=random_number,
        image=f'qr_codes/{filename}',
        is_active=True  # مهم علشان الـ IntegrityError اللي حصل قبل كده
    )

    image_url = f"{settings.MEDIA_URL}qr_codes/{filename}"
    return JsonResponse({'image_url': image_url})

#########################################################################

def student_attendance_page(request):
    return render(request, 'student_attendance.html')



def verify_qr_code(request):
    code = request.GET.get('qr_code_data')
    try:
        # تأكد من أن الكود عدد فقط
        if not code or not code.isdigit():
            return JsonResponse({'status': 'error', 'message': 'QR Code غير صالح (غير رقمي)'})

        qr_session = QRCodeSession.objects.get(
            code=int(code),
            is_active=True,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        )

        time_elapsed = timezone.now() - qr_session.created_at
        if time_elapsed > timedelta(minutes=1):
            return JsonResponse({'status': 'error', 'message': 'QR Code منتهي الصلاحية'})

        return JsonResponse({'status': 'success', 'message': 'QR Code سليم'})

    except QRCodeSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'QR Code غير صالح'})

    
#############################################################################

# النقاط الأربع تمثل حدود المبنى (بالترتيب يكون إما عقارب الساعة أو عكسها)
ZONE_POLYGON = [
    (31.2958300, 30.1013879),
    (30.1002912, 31.2986068),
    (30.1030259, 31.2995979),
    (31.2981099, 30.1036698),
]


def is_point_in_polygon(lat, lon, polygon):
    """
    راي كاستينج: هل النقطة (lat, lon) داخل المضلع polygon؟
    """
    x = lon
    y = lat
    inside = False
    n = len(polygon)

    p1x, p1y = polygon[0][1], polygon[0][0]  # lon, lat
    for i in range(n + 1):
        p2x, p2y = polygon[i % n][1], polygon[i % n][0]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                xinters = (y - p1y) * (p2x - p1x) / ((p2y - p1y) + 1e-10) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def verify_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = float(data.get("latitude"))
            lon = float(data.get("longitude"))
            
            inside = is_point_in_polygon(lat, lon, ZONE_POLYGON)
            
            if inside:
                return JsonResponse({'status': 'success', 'message': '✅ أنت داخل نطاق المبنى المحدد'})
            else:
                return JsonResponse({'status': 'error', 'message': '❌ أنت خارج حدود المبنى'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'❌ خطأ: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': '❌ الطلب غير صحيح'})
