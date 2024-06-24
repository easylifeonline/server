# ecommerce/views.py

from django.shortcuts import render
import os
from django.conf import settings

def index(request):
    return render(request, os.path.join(settings.BASE_DIR, 'frontend/build', 'index.html'))
