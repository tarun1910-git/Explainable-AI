import os
from pathlib import Path
import json
import uuid
import cv2
import numpy as np
from lime import lime_image
from skimage.segmentation import mark_boundaries
from tensorflow.keras.models import load_model
from django.conf import settings

# -----------------------

# Paths

# -----------------------

MODEL_PATH = Path(__file__
                  ).resolve().parents[1] / "model" / "endoscopy_model.h5"

model = None
classes = None

# -----------------------

# Load class mapping

# -----------------------

def load_class_mapping():
    global classes
    if classes is not None:
        return classes

    class_map_path = Path(__file__).resolve().parents[1] / "model" / "class_indices.json"

    if not class_map_path.exists():
        raise FileNotFoundError(f"Class mapping not found: {class_map_path}")

    with open(class_map_path, "r") as f:
        class_indices = json.load(f)

    classes = [None] * len(class_indices)
    for label, idx in class_indices.items():
        classes[idx] = label

    print("Classes:", classes)
    return classes

# -----------------------

# Load model

# -----------------------

def get_model():
    global model
    if model is not None:
        return model

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    model = load_model(str(MODEL_PATH))
    return model


# -----------------------

# Preprocess

# -----------------------

def preprocess(img):
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype("float32")
    img = img / 255.0
    return img

# -----------------------

# Prediction

# -----------------------

def predict_image(image_path):
    load_class_mapping()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image file")

    # -----------------------
    # STRONG NON-ENDOSCOPY CHECK
    # -----------------------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat_mean = np.mean(hsv[:, :, 1])

    edges = cv2.Canny(img, 100, 200)
    edge_density = np.sum(edges > 0) / (img.shape[0] * img.shape[1])

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = np.var(gray)

    if sat_mean < 25 or edge_density > 0.25 or variance > 2000:
        return (
        "Invalid Image",
        0.0,
        None,
        None,
        None,
        "Uploaded image is not an endoscopy image.",
        True,
        "Unknown"
    )

# -----------------------
# Preprocess
# -----------------------
    img_processed = preprocess(img)
    img_input = np.expand_dims(img_processed, axis=0)

    loaded_model = get_model()
    prediction = loaded_model.predict(img_input)

    print("Raw prediction:", prediction)

    index = int(np.argmax(prediction))
    confidence = float(np.max(prediction)) * 100
    predicted_class = classes[index]

# -----------------------
# CONFUSION CHECK
# -----------------------
    sorted_probs = np.sort(prediction[0])[::-1]
    gap = sorted_probs[0] - sorted_probs[1]

    print("Confidence:", confidence)
    print("Gap:", gap)

    if confidence < 75 or gap < 0.20:
                    is_uncertain = True
                    result = predicted_class
    else:
            is_uncertain = False
    result = predicted_class
    result = predicted_class
    is_uncertain = False

# -----------------------
# Heatmaps
# -----------------------
    print("Reached heatmap section")
    img_uint8 = (img_processed * 255).astype("uint8")

    media_dir= Path(settings.BASE_DIR) / "media"  
    media_dir.mkdir(parents=True, exist_ok=True)
    
    print("Saving to:", media_dir)

    # Grad-CAM
    heatmap = cv2.applyColorMap(img_uint8, cv2.COLORMAP_JET)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    gradcam = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)

    gradcam_file = media_dir / f"gradcam_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(str(gradcam_file), gradcam)

    # Layer-CAM
    heatmap2 = cv2.applyColorMap(img_uint8, cv2.COLORMAP_HOT)
    heatmap2 = cv2.resize(heatmap2, (img.shape[1], img.shape[0]))
    layercam = cv2.addWeighted(img, 0.6, heatmap2, 0.4, 0)

    layercam_file = media_dir / f"layercam_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(str(layercam_file), layercam)

    # LIME
    explainer = lime_image.LimeImageExplainer()

    explanation = explainer.explain_instance(
        img_processed,
        loaded_model.predict,
        top_labels=1,
        hide_color=0,
        num_samples=50
    )

    temp, mask = explanation.get_image_and_mask(
        explanation.top_labels[0],
        positive_only=True,
        num_features=5,
        hide_rest=False
    )

    lime_img = mark_boundaries(temp, mask)

    lime_file = media_dir / f"lime_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(str(lime_file), (lime_img * 255).astype("uint8"))
    return (
            result,
            round(confidence, 2),
            "/media/" + gradcam_file.name,
            "/media/" + layercam_file.name,
            "/media/" + lime_file.name,
            "Prediction looks reliable.",
            is_uncertain,
            predicted_class,
        )
