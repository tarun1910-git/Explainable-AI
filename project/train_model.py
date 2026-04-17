import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
import os

from project.settings import BASE_DIR

# -----------------------
# PATH 
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
train_dir = os.path.join(BASE_DIR, "dataset", "train")

# -----------------------
# DATA GENERATOR
# -----------------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=15,
    zoom_range=0.2,
    horizontal_flip=True
)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,   # 🔥 faster
    class_mode='categorical',
    subset='training'
)

val_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# -----------------------
# MODEL (MobileNetV2)
# -----------------------
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224,224,3)
)

# Freeze base layers
for layer in base_model.layers:
    layer.trainable = False

# Custom layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.5)(x)
output = Dense(train_data.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# Compile
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# -----------------------
# TRAIN
# -----------------------
model.fit(
    train_data,
    validation_data=val_data,
    epochs=5   # 🔥 reduced epochs
)

# -----------------------
# SAVE MODEL
# -----------------------
model.save("endoscopy_model.h5")

print("✅ Training completed successfully!")