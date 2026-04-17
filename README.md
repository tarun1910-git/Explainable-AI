<<<<<<< HEAD
https://drive.google.com/file/d/1F7pPq6KAdRgcC5f8MYT7zrqTryfw3PkN/view?usp=sharing
=======
# Explainable-AI
>>>>>>> a77968a52deabf7a90cf229e650ec57f8b602c87



# Explainable AI for Endoscopy

A web-based AI system for detecting gastrointestinal diseases from endoscopy images with explainability and medical report generation.

---

## 🚀 Overview

This project uses deep learning models to classify endoscopy images into four categories:

* Normal
* Bleeding
* Ulcer
* Polyp

It also provides explainable AI outputs using Grad-CAM, LIME, and Layer-CAM to help understand model decisions.

---

## ✨ Features

* 🧠 AI-based disease prediction (CNN / MobileNet / ResNet)
* 🔍 Explainability using:

  * Grad-CAM
  * Layer-CAM
  * LIME
* 📊 Confidence score with visualization
* 📄 Downloadable medical report (PDF)
* 👤 User and Admin dashboards
* 🕘 Prediction history tracking
* 🚫 Invalid image detection (non-endoscopy filtering)

---

## 🛠️ Tech Stack

* **Backend:** Django
* **Frontend:** HTML, CSS, Bootstrap
* **ML Framework:** TensorFlow / Keras
* **Image Processing:** OpenCV
* **Explainability:** LIME, Grad-CAM
* **PDF Generation:** ReportLab

---

## 🧪 How It Works

1. User uploads an endoscopy image
2. Image is preprocessed and passed to the trained model
3. Model predicts disease class with confidence score
4. Explainability maps are generated
5. Results are displayed with insights
6. User can download a medical-style PDF report

---

## 📁 Project Structure

```
project/
│── predictor/
│   ├── templates/
│   ├── static/
│   ├── views.py
│   ├── models.py
│   ├── predict.py
│
│── project/
│   ├── settings.py
│   ├── urls.py
│
│── manage.py
```

---

## ⚙️ Setup Instructions

1. Clone the repository:

```
git clone https://github.com/tarun1910-git/Explainable-AI.git
cd Explainable-AI
```

2. Create virtual environment:

```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run server:

```
python manage.py runserver
```

---

## 📌 Notes

* Model file is not included due to size limitations
* Media files (uploaded images) are not stored in repo
* Ensure model path is correctly configured before running

---

## 📸 Screenshots

*Add screenshots here (Home Page, Prediction Result, PDF Report)*

---

## 🚀 Future Improvements

* Real-time video analysis
* Integration with hospital systems
* Multi-disease classification
* Deployment on cloud

---

## 👨‍💻 Author

Tarun Ankana
GitHub: https://github.com/tarun1910-git

---

## 📄 License

This project is for academic and research purposes.

