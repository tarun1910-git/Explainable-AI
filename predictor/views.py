from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from datetime import datetime

from .predict import predict_image
from .models import Prediction
from .users import create_user
from reportlab.platypus import Image
import os
from django.conf import settings
import uuid

# PDF

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ------------------ UTILITY ------------------

def get_advice(confidence, is_admin):
    if is_admin:
        if confidence < 60:
            return f"Model confidence is low ({confidence:.1f}%). Findings may be unreliable."
        else:
            return f"Model confidence is high ({confidence:.1f}%). Verify clinically."
    else:
        if confidence < 60:
            return "The result is not very clear. Please consult a doctor."
        else:
            return "The result looks clear, but confirm with a doctor."

# ------------------ PAGES ------------------

def home(request):
        return render(request, "predictor/home.html")

def about(request):
        return render(request, "predictor/about.html")

def contact(request):
        if request.method == "POST":
            messages.success(request, "Message sent securely. We will reach you back shortly.")
            return redirect("contact")
            return render(request, "predictor/contact.html")

# ------------------ AUTH ------------------

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                messages.error(request, "Please provide correct user credentials.") 
                return render(request, "predictor/user_login.html") 
            # ✅ Allow normal user 
            
            login(request, user) 
            return redirect("user_dashboard")
        else: 
            messages.error(request, "Invalid username or password")
    return render(request, "predictor/user_login.html")

def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        user, error = create_user(username, email, password)

        if user:
            messages.success(request, "Account created successfully.")
            return redirect("user_login")

        messages.error(request, error)

    return render(request, "predictor/user_signup.html")


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid admin credentials")
            return render(request, "predictor/admin_login.html")

    return render(request, "predictor/admin_login.html")


def logout_view(request):
            logout(request)
            messages.info(request, "Logged out successfully.")
            return redirect("home")

# ------------------ DASHBOARDS ------------------

@login_required
def user_dashboard(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return render(request, "predictor/user_dashboard.html")

def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin_login")

    if not request.user.is_staff:
        return redirect("user_dashboard")

    if request.method == "POST":
        uploaded_file = request.FILES.get('image')

        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect("admin_dashboard")

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        image_path = fs.path(filename)

        try:
            result, confidence, gradcam_url, layercam_url, lime_url, advice, is_uncertain, predicted_class = predict_image(image_path)

            if result == "Invalid Image":
                messages.error(request, "Please upload a valid endoscopy image.")
                return redirect("admin_dashboard")

            advice = get_advice(confidence, True)

            Prediction.objects.create(
                user=request.user,
                image=uploaded_file,
                predicted_class=result,
                confidence=confidence
            )

            comparison = {
                "MobileNet": 0.75,
                "ResNet": 0.80,
                "CNN": 0.72,
                "F1 Score": 0.78,
                "Precision": 0.79,
                "Recall": 0.78,
            }

            return render(request, "predictor/model_comparison.html", {
                "comparison": comparison,
                "predicted_disease": result,
                "confidence": confidence,
                "gradcam_url": gradcam_url,
                "layercam_url": layercam_url,
                "lime_url": lime_url,
                "advice": advice,
            })

        except Exception as e:
            messages.error(request, f"Prediction failed: {e}")
            return redirect("admin_dashboard")

    return render(request, "predictor/admin_dashboard.html")


# ------------------ PREDICTION ------------------

def prediction_form(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in first.")
        return redirect("user_login")

    if request.method == "POST":
        uploaded_file = request.FILES.get('image')

        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect("predict")

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        image_url = fs.url(filename)
        image_path = fs.path(filename)

        try:
            result, confidence, gradcam_url, layercam_url, lime_url, advice, is_uncertain, predicted_class = predict_image(image_path)

            if result == "Invalid Image":
                messages.error(request, "Please upload a valid endoscopy image.")
                return redirect("predict")

            advice = get_advice(confidence, False)

            Prediction.objects.create(
                user=request.user,
                image=uploaded_file,
                predicted_class=result,
                confidence=confidence
            )
            print("IMAGE URL:", image_url)
            print("GRADCAM URL:", gradcam_url)

            return render(request, "predictor/prediction_result.html", {
                "result": result,
                "confidence": confidence,
                "image_url": image_url,
                "gradcam_url": gradcam_url,
                "layercam_url": layercam_url,
                "lime_url": lime_url,
                "advice": advice,
                "is_uncertain": is_uncertain,
                "predicted_class": predicted_class,
            })

        except Exception as e:
            messages.error(request, f"Prediction failed: {e}")
            return redirect("predict")

    return render(request, "predictor/prediction_form.html")


def prediction_history(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    predictions = Prediction.objects.filter(user=request.user)
    return render(request, "predictor/prediction_history.html", {"predictions": predictions})


@staff_member_required
def admin_history(request):
    predictions = Prediction.objects.all().order_by('-created_at')
    return render(request, "predictor/admin_history.html", {"predictions": predictions})

# ------------------ METRICS ------------------

def resnet_metrics(request):
    metrics = {
        "Loss": 0.067,
        "Accuracy": 0.80,
        "Precision": 0.79,
        "Recall": 0.78,
        "F1 Score": 0.78
    }
    return render(request, "predictor/resnet_metrics.html", {"metrics": metrics})

def mobilenet_metrics(request):
    metrics = {
        "Loss": 0.08,
        "Accuracy": 0.75,
        "Precision": 0.73,
        "Recall": 0.72,
        "F1 Score": 0.71
    }
    return render(request, "predictor/mobilenet_metrics.html", {"metrics": metrics})

# ------------------ PDF REPORT ------------------

def generate_pdf(request, result, confidence, advice, username, gradcam_path=None):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Endoscopy_Report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    content = []

    # 🏥 LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
    if os.path.exists(logo_path):
        content.append(Image(logo_path, width=100, height=50))
        content.append(Spacer(1, 10))

    # TITLE
    content.append(Paragraph("<b>Endoscopy AI Diagnostic Report</b>", styles['Title']))
    content.append(Spacer(1, 20))

    # 🆔 Patient ID
    patient_id = str(uuid.uuid4())[:8]

    content.append(Paragraph(f"<b>Patient ID:</b> {patient_id}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Patient Name:</b> {username}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles['Normal']))
    content.append(Spacer(1, 15))

    content.append(Paragraph(f"<b>Predicted Condition:</b> {result}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Confidence:</b> {confidence}%", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Medical Insight:</b> {advice}", styles['Normal']))
    content.append(Spacer(1, 20))

    # 🖼️ Grad-CAM Image
    if gradcam_path and os.path.exists(gradcam_path):
        content.append(Paragraph("<b>Grad-CAM Analysis:</b>", styles['Heading3']))
        content.append(Spacer(1, 10))
        content.append(Image(gradcam_path, width=300, height=200))
        content.append(Spacer(1, 20))

    # FOOTER
    content.append(Paragraph(
        "This report is generated by an AI system. Please consult a doctor.",
        styles['Italic']
    ))

    doc.build(content)
    return response

def download_report(request):
    result = request.GET.get('result', 'N/A')
    confidence = request.GET.get('confidence', '0')
    advice = request.GET.get('advice', 'N/A')

    username = request.user.username if request.user.is_authenticated else "Guest"

    # ⚠️ IMPORTANT: convert URL → file path
    gradcam_url = request.GET.get('gradcam_url')

    gradcam_path = None
    if gradcam_url:
        filename = gradcam_url.split('/')[-1]
        gradcam_path = os.path.join(settings.MEDIA_ROOT, filename)
        print("DEBUG PATH:", gradcam_path)
    return generate_pdf(request, result, confidence, advice, username, gradcam_path)