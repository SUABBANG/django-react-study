from django.contrib import messages
from django.shortcuts import render

# Create your views here.
def index(request):
    messages.debug(request, 'Debug message')
    messages.info(request, 'Info message')
    messages.success(request, 'Success message')
    messages.warning(request, 'Warning message')
    messages.error(request, 'Error message')
    return render(request, template_name="core/index.html")