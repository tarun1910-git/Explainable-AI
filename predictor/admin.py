from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout   # ✅ import this
from django.contrib import admin
from .models import Prediction


def index(req):
    return render(req, 'index.html')


def about(req):
    return render(req, 'about.html')


def contact(req):
    return render(req, 'contact.html')

def logout(req):
    logout_user(req)
    messages.success(req, "Logged out successfully")
    return redirect('alogin')   # or 'index'


def alogin(req):
    if req.method == 'POST':
        name = req.POST.get('name')
        password = req.POST.get('password')

        if name == 'admin' and password == 'admin':
            messages.success(req, 'You are logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(req, 'Invalid admin credentials. Please try again.')
            return redirect('alogin')

    return render(req, 'alogin.html')


def dashboard(req):
    return render(req, 'dashboard.html')


# ✅ Proper logout view
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('alogin')   # or 'index'

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_class', 'confidence', 'created_at')
    list_filter = ('predicted_class', 'created_at')
    search_fields = ('user__username', 'predicted_class')