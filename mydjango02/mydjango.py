import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.urls import path
settings.configure(ROOT_URLCONF=__name__, DEBUG=True, SECRET_KEY="secret")
django.setup()
# View 함수 : HTTP 요청이 올 때마다 호출 되어, 요청을 처리하여 응답을 생성/반환하는 함수
def index(request):
 return HttpResponse("""
     <html>
     <body>
     HELLO DJANGO
     </body>
     </html>
     """)
# View 함수
def hello(request):
    return HttpResponse("hello django")
urlpatterns = [
     path("", index), # http://localhost:8000 요청에 매핑
     path("hello/", hello), # http://localhost:8000/hello/ 요청에 매핑
]
execute_from_command_line(sys.argv)